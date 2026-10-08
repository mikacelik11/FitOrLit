import sqlite3

import pytest

import database

from onboard import UserStore
from calc import (
    bmi_calc,
    bulk_cal,
    cut_cal,
    female_BMR,
    maintenace_cal,
    male_BMR,
)


@pytest.fixture # the function underneath prepares test data 
def store(tmp_path):
    # tmp_path is built into pytest. Before the test runs, pytest creates a new temperary directory
    database_path = tmp_path / "test.db"
    return UserStore(database_path) # this creates a userstore connected to the temp database

# onboard.py
# notice the store parameter it performs the process automatically
# test requests store
# pytest finds store fixture
# fixture requests tmp_path
# pytest creates a temp directory
# fixture creates UserStore using test.db
# Pytest passes that UserStore into test_login
def test_new_store_starts_logged_out(store):
    assert store.current_user is None
    assert store.is_logged_in() is False
    


# This test is to check if register function works and a new user is registered
def test_new_username_is_accepted(store): 
    result = store.register("mika", "123456@")
    user = store.find_user("mika")

    assert result is True
    assert user is not None
    assert user.username == "mika"

# Now if there are duplicate username the person should be reprompted to make a different password
# and should not be registered unless it is a unique username.  
def test_duplicate_username_is_rejected(store):
    first_result = store.register("mika", "123456@")
    second_result = store.register("mika", "different@123")

    assert first_result is True
    assert second_result is False
    assert store.find_user("mika") is not None

    
## make sure that partial username is treated as a duplicate 
# this was an issue with my previous code 
def test_partial_username_is_not_treated_as_duplicate(store):
    store.register("samantha", "123456@")

    assert store.find_user("samantha") is not None
    assert store.find_user("sam") is None
    
def test_find_user(store):
  
    store.register('luka', '123456@')
    user = store.find_user('luka')
    
    assert user is not None
    assert user.username == 'luka'
    

# Make sure if username is right but the password is differen tthen we can't find the user
def test_find_user_returns_none_for_unknown_user(store):

    store.register("luka", "123457@")

    user = store.find_user("jerry")

    assert user is None
    
# make sure login is successful  and our current user is the one we logged in with
def test_login(store):

    store.register('joe', '123456@')
    expected_user = store.find_user('joe')
    
    result = store.login('joe', '123456@')
    
    assert result is True
    assert store.current_user is not None
    assert store.current_user.username == "joe"
    assert store.is_logged_in() is True
    
# test checks the login in with different password doesn't work
def test_failed_login_does_not_set_current_user(store):

    store.register("joe", "123456@")

    result = store.login("joe", "456")

    assert result is False
    assert store.current_user is None
    assert store.is_logged_in() is False


# test log out and makes sure that if logout is called then current user is set to None.
def test_logout_clears_current_user(store):

    store.register("joe", "123456@")
    store.login("joe", "123456@")

    store.logout()

    assert store.current_user is None
    assert store.is_logged_in() is False


# database.py: partial health profiles
@pytest.fixture
def health_user(store):
    assert store.register("health_user", "123456@") is True
    assert store.login("health_user", "123456@") is True
    return store.current_user


def test_logged_in_user_has_database_id(store, health_user):
    row = database.get_user_by_username("health_user", store.database_path)
    assert health_user.id == row[0]
    



def test_age_can_be_saved_without_other_answers(store, health_user):
    assert database.save_health_data(health_user.id, store.database_path, age=25) is True

    connection = sqlite3.connect(store.database_path)
    try:
        row = connection.execute(
            """
            SELECT user_id, age, height_cm, weight_kg,
                   activity_factor, goal, bmr_formula, created_at
            FROM users_health_data WHERE user_id = ?
            """,
            (health_user.id,),
        ).fetchone()
    finally:
        connection.close()

    assert row[:7] == (health_user.id, 25, None, None, None, None, None)
    assert row[7] is not None


def test_saving_age_again_updates_only_that_answer(store, health_user):
    assert database.save_health_data(health_user.id, store.database_path, age=25) is True
    assert database.save_health_data(
        health_user.id, store.database_path, height_cm=175.5, weight_kg=70.5
    ) is True

    connection = sqlite3.connect(store.database_path)
    try:
        created_at = connection.execute(
            "SELECT created_at FROM users_health_data WHERE user_id = ?",
            (health_user.id,),
        ).fetchone()[0]
    finally:
        connection.close()

    assert database.save_health_data(health_user.id, store.database_path, age=26) is True

    connection = sqlite3.connect(store.database_path)
    try:
        rows = connection.execute(
            "SELECT user_id, age, height_cm, weight_kg, created_at FROM users_health_data"
        ).fetchall()
    finally:
        connection.close()

    assert rows == [(health_user.id, 26, 175.5, 70.5, created_at)]


@pytest.mark.parametrize("age", [0, -1, 25.5, "25", "abc", True, None])
def test_invalid_age_does_not_overwrite_saved_age(store, health_user, age):
    assert database.save_health_data(health_user.id, store.database_path, age=25) is True
    assert database.save_health_data(health_user.id, store.database_path, age=age) is False

    connection = sqlite3.connect(store.database_path)
    try:
        row = connection.execute(
            "SELECT age FROM users_health_data WHERE user_id = ?",
            (health_user.id,),
        ).fetchone()
    finally:
        connection.close()

    assert row == (25,)


@pytest.mark.parametrize("user_id", [None, True, "1", 0, -1, 1.5, 999999])
def test_health_data_cannot_be_saved_for_invalid_or_unknown_user(store, health_user, user_id):
    assert database.save_health_data(user_id, store.database_path, age=25) is False

    connection = sqlite3.connect(store.database_path)
    try:
        count = connection.execute("SELECT COUNT(*) FROM users_health_data").fetchone()[0]
    finally:
        connection.close()

    assert count == 0


def test_age_is_saved_to_the_correct_user(store, health_user):
    assert store.register("second_user", "123456@") is True
    second_user = store.find_user("second_user")

    assert database.save_health_data(health_user.id, store.database_path, age=25) is True
    assert database.save_health_data(second_user.id, store.database_path, age=40) is True

    connection = sqlite3.connect(store.database_path)
    try:
        rows = connection.execute(
            "SELECT user_id, age FROM users_health_data ORDER BY user_id"
        ).fetchall()
    finally:
        connection.close()

    assert rows == [(health_user.id, 25), (second_user.id, 40)]


def test_health_initialization_preserves_existing_answers(store, health_user):
    assert database.save_health_data(health_user.id, store.database_path, age=25) is True

    database.initialize_database(store.database_path)
    reopened_store = UserStore(store.database_path)
    assert reopened_store.login("health_user", "123456@") is True
    assert reopened_store.current_user.id == health_user.id

    connection = sqlite3.connect(store.database_path)
    try:
        row = connection.execute(
            "SELECT age FROM users_health_data WHERE user_id = ?",
            (health_user.id,),
        ).fetchone()
    finally:
        connection.close()

    assert row == (25,)


@pytest.mark.parametrize(
    "field, value, column_index",
    [
        ("age", 25, 0),
        ("height_cm", 175.5, 1),
        ("weight_kg", 70.5, 2),
        ("activity_factor", 1.55, 3),
        ("goal", "cut", 4),
        ("bmr_formula", "female", 5),
    ],
)
def test_any_single_answer_can_start_a_profile(store, health_user, field, value, column_index):
    assert database.save_health_data(
        health_user.id, store.database_path, **{field: value}
    ) is True

    connection = sqlite3.connect(store.database_path)
    try:
        row = connection.execute(
            """
            SELECT age, height_cm, weight_kg, activity_factor, goal, bmr_formula
            FROM users_health_data WHERE user_id = ?
            """,
            (health_user.id,),
        ).fetchone()
    finally:
        connection.close()

    expected = [None] * 6
    expected[column_index] = value
    assert row == tuple(expected)


def test_health_answers_can_be_saved_one_at_a_time(store, health_user):
    answers = {
        "age": 25,
        "height_cm": 175.5,
        "weight_kg": 70.5,
        "activity_factor": 1.55,
        "goal": "maintain",
        "bmr_formula": "male",
    }
    for field, value in answers.items():
        assert database.save_health_data(
            health_user.id, store.database_path, **{field: value}
        ) is True

    # Revising later answers must not erase the earlier ones.
    assert database.save_health_data(
        health_user.id, store.database_path, weight_kg=71.5, goal="bulk"
    ) is True

    connection = sqlite3.connect(store.database_path)
    try:
        rows = connection.execute(
            """
            SELECT user_id, age, height_cm, weight_kg, activity_factor, goal, bmr_formula
            FROM users_health_data
            """
        ).fetchall()
    finally:
        connection.close()

    assert rows == [(health_user.id, 25, 175.5, 71.5, 1.55, "bulk", "male")]


def test_all_health_answers_can_be_saved_together(store, health_user):
    assert database.save_health_data(
        health_user.id,
        database_path=store.database_path,
        age=25,
        height_cm=175,
        weight_kg=70,
        activity_factor=1.55,
        goal="cut",
        bmr_formula="female",
    ) is True

    connection = sqlite3.connect(store.database_path)
    try:
        row = connection.execute(
            """
            SELECT age, height_cm, weight_kg, activity_factor, goal, bmr_formula
            FROM users_health_data WHERE user_id = ?
            """,
            (health_user.id,),
        ).fetchone()
    finally:
        connection.close()

    assert row == (25, 175, 70, 1.55, "cut", "female")


def test_none_skips_an_answer_instead_of_erasing_it(store, health_user):
    assert database.save_health_data(
        health_user.id, store.database_path, age=25, goal="maintain"
    ) is True
    assert database.save_health_data(
        health_user.id, store.database_path, age=None, goal=None, height_cm=175.5
    ) is True

    connection = sqlite3.connect(store.database_path)
    try:
        row = connection.execute(
            "SELECT age, height_cm, goal FROM users_health_data WHERE user_id = ?",
            (health_user.id,),
        ).fetchone()
    finally:
        connection.close()

    assert row == (25, 175.5, "maintain")


def test_saving_without_answers_does_not_create_a_profile(store, health_user):
    assert database.save_health_data(health_user.id, store.database_path) is False
    assert database.save_health_data(
        health_user.id, store.database_path,
        age=None, height_cm=None, weight_kg=None,
        activity_factor=None, goal=None, bmr_formula=None,
    ) is False

    connection = sqlite3.connect(store.database_path)
    try:
        count = connection.execute("SELECT COUNT(*) FROM users_health_data").fetchone()[0]
    finally:
        connection.close()

    assert count == 0


@pytest.mark.parametrize(
    "invalid_answers",
    [
        {"age": 0},
        {"age": 25.5},
        {"age": True},
        {"age": 2 ** 63},
        {"height_cm": 0},
        {"height_cm": -175},
        {"height_cm": "175"},
        {"height_cm": True},
        {"height_cm": float("nan")},
        {"height_cm": float("inf")},
        {"height_cm": 2 ** 63},
        {"weight_kg": -1},
        {"weight_kg": "70"},
        {"weight_kg": False},
        {"weight_kg": float("nan")},
        {"weight_kg": float("inf")},
        {"activity_factor": 0},
        {"activity_factor": "1.55"},
        {"activity_factor": True},
        {"activity_factor": float("nan")},
        {"activity_factor": float("inf")},
        {"goal": "unknown"},
        {"goal": ""},
        {"goal": ["cut"]},
        {"bmr_formula": "unknown"},
        {"bmr_formula": 1},
        {"bmr_formula": ["male"]},
    ],
)
def test_invalid_health_answer_rejects_the_entire_save(store, health_user, invalid_answers):
    assert database.save_health_data(
        health_user.id, store.database_path, age=25, goal="maintain"
    ) is True

    # Even the valid age/goal changes must not be saved alongside a bad answer.
    answers = {"age": 26, "goal": "bulk", **invalid_answers}
    assert database.save_health_data(
        health_user.id, store.database_path, **answers
    ) is False

    connection = sqlite3.connect(store.database_path)
    try:
        rows = connection.execute(
            """
            SELECT user_id, age, height_cm, weight_kg, activity_factor, goal, bmr_formula
            FROM users_health_data
            """
        ).fetchall()
    finally:
        connection.close()

    assert rows == [(health_user.id, 25, None, None, None, "maintain", None)]
    
# get_health_data: loading saved profiles
def test_get_health_data_returns_none_before_any_answers(store, health_user):
    # The account exists, but its health profile has not been created yet.
    profile = database.get_health_data(health_user.id, store.database_path)

    assert profile is None


def test_get_health_data_returns_none_for_unknown_user(store, health_user):
    # Another saved profile must not be returned for an unknown user ID.
    assert database.save_health_data(health_user.id, store.database_path, age=25) is True

    profile = database.get_health_data(999999, store.database_path)

    assert profile is None


def test_get_health_data_returns_age_only_profile(store, health_user):
    assert database.save_health_data(health_user.id, store.database_path, age=25) is True

    profile = database.get_health_data(health_user.id, store.database_path)

    assert isinstance(profile, tuple)
    assert len(profile) == 8
    # Row order: user ID, age, height, weight, activity, goal, formula, timestamp.
    assert profile[:7] == (health_user.id, 25, None, None, None, None, None)
    assert isinstance(profile[7], str)
    assert profile[7]  # The creation timestamp should not be empty.


def test_get_health_data_returns_complete_profile(store, health_user):
    assert database.save_health_data(
        health_user.id,
        database_path=store.database_path,
        age=25,
        height_cm=175.5,
        weight_kg=70.5,
        activity_factor=1.55,
        goal="cut",
        bmr_formula="female",
    ) is True

    profile = database.get_health_data(health_user.id, store.database_path)

    assert profile is not None
    assert profile[:7] == (health_user.id, 25, 175.5, 70.5, 1.55, "cut", "female")


def test_get_health_data_keeps_users_profiles_separate(store, health_user):
    assert store.register("second_user", "123456@") is True
    second_user = store.find_user("second_user")
    assert second_user is not None
    assert database.save_health_data(health_user.id, store.database_path, age=25) is True
    assert database.save_health_data(
        second_user.id, store.database_path, age=40, height_cm=180
    ) is True

    first_profile = database.get_health_data(health_user.id, store.database_path)
    second_profile = database.get_health_data(second_user.id, store.database_path)

    assert first_profile is not None
    assert second_profile is not None
    assert first_profile[:7] == (health_user.id, 25, None, None, None, None, None)
    assert second_profile[:7] == (second_user.id, 40, 180, None, None, None, None)


def test_get_health_data_returns_updated_answers(store, health_user):
    assert database.save_health_data(health_user.id, store.database_path, age=25) is True
    original_profile = database.get_health_data(health_user.id, store.database_path)
    assert original_profile is not None

    assert database.save_health_data(
        health_user.id, store.database_path, age=26, height_cm=175.5
    ) is True
    updated_profile = database.get_health_data(health_user.id, store.database_path)

    assert updated_profile is not None
    assert updated_profile[:7] == (health_user.id, 26, 175.5, None, None, None, None)
    assert updated_profile[7] == original_profile[7]


def test_get_health_data_reads_the_requested_database(store, health_user, tmp_path):
    other_store = UserStore(tmp_path / "other.db")
    assert other_store.register("health_user", "123456@") is True
    other_user = other_store.find_user("health_user")
    assert other_user is not None
    # IDs can be the same in different databases, but their answers can differ.
    assert other_user.id == health_user.id
    assert database.save_health_data(health_user.id, store.database_path, age=25) is True
    assert database.save_health_data(other_user.id, other_store.database_path, age=40) is True

    first_profile = database.get_health_data(health_user.id, store.database_path)
    other_profile = database.get_health_data(other_user.id, other_store.database_path)

    assert first_profile is not None
    assert other_profile is not None
    assert first_profile[1] == 25
    assert other_profile[1] == 40


def test_get_health_data_loads_answers_after_reopening_store(store, health_user):
    assert database.save_health_data(health_user.id, store.database_path, age=25) is True
    expected_profile = database.get_health_data(health_user.id, store.database_path)
    assert expected_profile is not None

    reopened_store = UserStore(store.database_path)
    profile = database.get_health_data(health_user.id, reopened_store.database_path)

    assert profile == expected_profile


# Calc.py
def test_bmi():
    result = bmi_calc(70, 1.75)
    assert result == pytest.approx(22.86, abs=0.01)


def test_male_bmr():
    result = male_BMR(80, 180, 30)
    assert result == 1780


def test_female_bmr():
    result = female_BMR(60, 165, 30)
    assert result == 1320.25


def test_maintenance_calories():
    result = maintenace_cal(1780, 1.55)
    assert result == pytest.approx(2759)


def test_cut_calories_with_ten_percent_deficit():
    result = cut_cal(2000, 0.10)
    assert result == pytest.approx(1800)


def test_bulk_calories_with_ten_percent_surplus():
    result = bulk_cal(2000, 0.10)
    assert result == pytest.approx(2200)
