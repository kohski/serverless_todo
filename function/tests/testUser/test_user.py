import pytest
from copy import deepcopy
from user import User, UserNotFoundError, NotAuthorizedError
from jsonschema import ValidationError


@pytest.fixture
def typical_user():
    return {
        'id': '2340725f-125b-429b-ba17-6c598b539b63',
        'email': 'hoge@hoge.com',
        'family_name': '田中',
        'given_name': '太郎'
    }


class TestUser:

    def test_user(self, typical_user):
        temp_user = User(
            **typical_user
        )
        assert hasattr(temp_user, 'id')
        assert hasattr(temp_user, 'email')
        assert hasattr(temp_user, 'family_name')
        assert hasattr(temp_user, 'given_name')

    def test_raise_invalid_id(self, typical_user):
        copied_typical_user = deepcopy(typical_user)
        copied_typical_user['id'] = 'invalid_user_id'
        with pytest.raises(ValidationError):
            User(**copied_typical_user)

    def test_raise_invalid_email(self, typical_user):
        copied_typical_user = deepcopy(typical_user)
        copied_typical_user['email'] = 'invalid_email'
        with pytest.raises(ValidationError):
            User(**copied_typical_user)

    def test_raise_invalid_short_family_name(self, typical_user):
        copied_typical_user = deepcopy(typical_user)
        copied_typical_user['family_name'] = ''
        with pytest.raises(ValidationError):
            User(**copied_typical_user)

    def test_raise_invalid_long_family_name(self, typical_user):
        copied_typical_user = deepcopy(typical_user)
        copied_typical_user['family_name'] = 'a' * 101
        with pytest.raises(ValidationError):
            User(**copied_typical_user)

    def test_raise_invalid_short_given_name(self, typical_user):
        copied_typical_user = deepcopy(typical_user)
        copied_typical_user['given_name'] = ''
        with pytest.raises(ValidationError):
            User(**copied_typical_user)

    def test_raise_invalid_long_given_name(self, typical_user):
        copied_typical_user = deepcopy(typical_user)
        copied_typical_user['given_name'] = 'a' * 101
        with pytest.raises(ValidationError):
            User(**copied_typical_user)


class TestLogin:

    def test_username_login(self, idp_create_init_data):
        res = User.login('existing_user_id', 'Test1234#')
        assert 'AuthenticationResult' in res and 'IdToken' in res['AuthenticationResult']

    def test_raise_not_existing_user(self, idp_create_init_data):
        with pytest.raises(UserNotFoundError):
            User.login('not_existing_user_id', 'Test1234#')

    def test_raise_not_valid_password(self, idp_create_init_data):
        with pytest.raises(NotAuthorizedError):
            User.login('existing_user_id', 'not_valid_password')
