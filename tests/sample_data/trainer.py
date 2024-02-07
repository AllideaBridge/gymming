from app import Trainer

sample_trainer = Trainer(
    user_id=1,  # 유효한 Users 모델의 user_id를 사용해야 합니다.
    center_id=None,  # Center 모델의 center_id를 사용하거나 None으로 설정할 수 있습니다.
    trainer_pr_url="http://example.com/trainer/pr",
    trainer_pt_price=50000,
    certification="Certified Personal Trainer",
    trainer_education="Bachelor's Degree in Sports Science"
)