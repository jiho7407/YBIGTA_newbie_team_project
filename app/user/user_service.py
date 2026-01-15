from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        """
        로그인 함수
        1. 이메일로 유저 조회
        2. 유저가 없으면 예외처리
        3. 비밀번호 비교
        4. 일치하지 않으면 예외처리
        5. 유저 반환
        """
        
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            raise ValueError("User not Found.")
        if user.password != user_login.password:
            raise ValueError("Invalid ID/PW")
        return user
        
    def register_user(self, new_user: User) -> User:
        """
        회원가입 함수
        1. 이메일로 유저 조회
        2. 유저가 이미 있으면 예외처리
        3. 유저 저장
        4. 저장된 유저 반환
        """

        if self.repo.get_user_by_email(new_user.email):
            raise ValueError("User already Exists.")

        else:
            new_user = self.repo.save_user(new_user)

        return new_user

    def delete_user(self, email: str) -> User:
        """
        회원탈퇴 함수
        1. 이메일로 유저 조회
        2. 유저가 없으면 예외처리
        3. 유저 삭제
        4. 삭제된 유저 반환
        """

        user = self.repo.get_user_by_email(email)
        if user is None:
            raise ValueError("User not Found.")
        
        else:
            deleted_user = self.repo.delete_user(user)

        return deleted_user

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        """
        비밀번호 변경 함수
        1. 이메일로 유저 조회
        2. 유저가 없으면 예외처리
        3. 비밀번호 변경
        4. 변경된 유저 반환
        """

        target_user = self.repo.get_user_by_email(user_update.email)
        if not target_user:
            raise ValueError("User not Found.")

        target_user.password = user_update.new_password
        updated_user = self.repo.save_user(target_user)
        return updated_user