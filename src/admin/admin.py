from sqladmin import Admin, ModelView
from src.users.models import User
from src.workouts.models import Workout, Exercise, Set, Exercise_photo, DifficultyWorkout
from src.core.database import engine
from .auth import authentication_backend


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, "role.name", User.first_name, User.last_name, User.registered_at]
    column_sortable_list = ["role.name", User.registered_at]
    column_searchable_list = [User.email]
    can_create = False
    icon = "fa-solid fa-user"


class WorkoutAdmin(ModelView, model=Workout):
    column_list = [Workout.id, "user.first_name", Workout.name, Workout.is_public, Workout.created_at,
                   Workout.difficulty]
    column_sortable_list = \
        [Workout.id, "user.first_name", Workout.name, Workout.is_public, Workout.created_at, Workout.difficulty]
    column_searchable_list = [Workout.name]
    can_create = False


class ExerciseAdmin(ModelView, model=Exercise):
    column_list = [Exercise.id, Exercise.name, "workout.name"]
    column_sortable_list = [Exercise.id, "workout.name"]
    can_create = False


class SetAdmin(ModelView, model=Set):
    column_list = [Set.id, "exercise.name"]
    can_create = False
    can_edit = False
    can_view_details = False


class PhotoAdmin(ModelView, model=Exercise_photo):
    column_list = [Exercise_photo.id, Exercise_photo.photo]
    can_create = False


class DifficultyWorkoutAdmin(ModelView, model=DifficultyWorkout):
    column_list = [DifficultyWorkout.id, DifficultyWorkout.difficulty]


def init_admin(app):
    admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(WorkoutAdmin)
    admin.add_view(ExerciseAdmin)
    admin.add_view(SetAdmin)
    admin.add_view(PhotoAdmin)
    admin.add_view(DifficultyWorkoutAdmin)
    return admin
