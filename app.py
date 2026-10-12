import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# The Owner lives in session_state so it survives Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        elif any(p.name.lower() == pet_name.strip().lower() for p in owner.pets):
            st.error(f"You already have a pet named {pet_name.strip()}.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species, int(age)))
            st.success(f"Added {pet_name.strip()}!")

st.subheader("Add a task")
if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task", clear_on_submit=True):
        target = st.selectbox("Pet", [p.name for p in owner.pets])
        description = st.text_input("Task description", placeholder="Morning walk")
        task_time = st.time_input("Time", value=None)
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            if not description.strip() or task_time is None:
                st.error("Please enter a description and a time.")
            else:
                pet = next(p for p in owner.pets if p.name == target)
                pet.add_task(Task(description.strip(), task_time.strftime("%H:%M"), frequency))
                st.success(f"Added '{description.strip()}' for {target}.")

st.divider()
st.subheader("Today's schedule")
if st.button("Show schedule"):
    schedule = scheduler.get_todays_schedule()
    if not schedule:
        st.info("Nothing scheduled for today.")
    else:
        st.table(
            [
                {"Time": t.time, "Pet": t.pet_name, "Task": t.description,
                 "Repeats": t.frequency, "Done": t.completed}
                for t in schedule
            ]
        )
