# PawPal+ Project Reflection

## 1. System Design

**1a. Initial Design**

My first UML (`diagrams/uml_draft.mmd`) has four classes, each with one job:

- **Task** holds one piece of care work: a description, an `HH:MM` time, a frequency (`once`, `daily`, `weekly`), a completed flag and a due date. It only knows how to mark itself complete.
- **Pet** (name, species, age) owns a list of Tasks and can add one or list the pending ones. A task belongs to exactly one pet, so the pet is the natural container.
- **Owner** owns a list of Pets and can flatten every pet's tasks into one list (`get_all_tasks`). It is the single entry point to the data.
- **Scheduler** holds no data of its own. It takes an Owner and does the "thinking": today's schedule, sorting, filtering, conflict detection and recurrence.

Relationships: Owner 1-* Pet, Pet 1-* Task, and Scheduler points at Owner.

I kept the algorithms out of the data classes on purpose. Task, Pet and Owner stay simple containers that are easy to test, and anything that looks across several pets lives in one place, the Scheduler. Times are `HH:MM` strings so they sort lexicographically and are easy to show in a UI.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
