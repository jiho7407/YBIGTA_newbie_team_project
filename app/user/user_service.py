from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        
        ## TODO
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            raise ValueError("User not Found.")
        if user.password != user_login.password:
            raise ValueError("Invalid ID/PW")
        return user
        
    def register_user(self, new_user: User) -> User:

        ## TODO
        if new_user.email is None:
            raise ValueError("회원가입에 실패했습니다.")

        elif new_user.email == "admin":
            raise ValueError("회원가입에 실패했습니다.")
        
        elif self.repo.get_user_by_email(new_user.email) is None:
            raise ValueError("회원가입에 실패했습니다.")

        else:
            new_user = self.repo.save_user(new_user)

        return new_user

    def delete_user(self, email: str) -> User:

        ## TODO
        user = self.repo.get_user_by_email(email)
        if user is None:
            raise ValueError("User not Found.")
        
        else:
            deleted_user = self.repo.delete_user(user)

        return deleted_user

    def update_user_pwd(self, user_update: UserUpdate) -> User:

        ## TODO
        target_user = self.repo.get_user_by_email(user_update.email)
        if not target_user:
            raise ValueError("User not Found.")

        target_user.password = user_update.new_password
        updated_user = self.repo.save_user(target_user)
        return updated_user