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
st.subheader("Schedule")
if st.button("Show schedule"):
    st.session_state.show_schedule = True

if st.session_state.get("show_schedule"):
    for msg in st.session_state.pop("flash", []):
        st.success(msg)

    # Conflicts first so they are hard to miss.
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No scheduling conflicts.")

    col_pet, col_status = st.columns(2)
    pet_choice = col_pet.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
    status_choice = col_status.selectbox("Status", ["All", "Pending", "Completed"])
    completed = {"All": None, "Pending": False, "Completed": True}[status_choice]
    tasks = scheduler.sort_by_time(
        scheduler.filter_tasks(None if pet_choice == "All" else pet_choice, completed)
    )
    if tasks:
        st.table(
            [
                {"Date": t.due_date.isoformat(), "Time": t.time, "Pet": t.pet_name,
                 "Task": t.description, "Repeats": t.frequency,
                 "Status": "Done" if t.completed else "Pending"}
                for t in tasks
            ]
        )
    else:
        st.info("No tasks match these filters.")

    st.subheader("Complete a task")
    pending = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if pending:
        labels = [f"{t.due_date} {t.time} - {t.pet_name}: {t.description}" for t in pending]
        picked = st.selectbox("Pending task", range(len(pending)), format_func=lambda i: labels[i])
        if st.button("Mark complete"):
            task = pending[picked]
            new_task = scheduler.handle_recurring(task)
            msgs = [f"Completed '{task.description}' for {task.pet_name}."]
            if new_task:
                msgs.append(f"Next {task.frequency} occurrence scheduled for "
                            f"{new_task.due_date} at {new_task.time}.")
            st.session_state.flash = msgs
            st.rerun()  # redraw so the tables reflect the change
    else:
        st.info("No pending tasks.")
