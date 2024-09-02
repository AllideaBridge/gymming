from database import db


# todo.txt : (trainer_id, week_day)는 유니크 해야 함. (조인조건이 유니크 하지 않으면 중복 데이터 발생) 로직으로 막기 vs 디비 키 설정 하기.
class TrainerAvailability(db.Model):
    trainer_availability_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'), nullable=False)
    week_day = db.Column(db.Integer, nullable=False)  # 예: 월요일부터 0,1,2,3,4,5,6
    start_time = db.Column(db.Time, nullable=False)  # 근무 가능 시작 시간
    end_time = db.Column(db.Time, nullable=False)
    possible_lesson_cnt = db.Column(db.Integer, nullable=False)

    def __init__(self, trainer_id, week_day, start_time, end_time, possible_lesson_cnt):
        self.trainer_id = trainer_id
        self.week_day = week_day
        self.start_time = start_time
        self.end_time = end_time
        self.possible_lesson_cnt = possible_lesson_cnt
