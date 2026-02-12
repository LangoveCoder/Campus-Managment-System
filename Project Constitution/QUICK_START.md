# Quick Start Guide - Get Building Today

**Time to Read:** 5 minutes  
**Time to First Code:** 30 minutes  
**Purpose:** Get you from "I have documentation" to "I'm building" NOW  

---

## 🚦 Current Status Check

**Where You Are:**
- ✅ Architecture designed and validated
- ✅ Constitution written (v2.0 - final)
- ✅ Task list created (120+ tasks)
- ✅ Documentation complete
- ⬜ Environment set up
- ⬜ First line of code written

**Where You're Going:**
- Week 1: Core identity models in database
- Week 2: Authorization engine working
- Week 3: Campus isolation enforced
- Month 2: Biometric system functional
- Month 3: First college using the system

---

## ⚡ The 30-Minute Setup

### Step 1: Install Prerequisites (15 minutes)

**On Ubuntu/Debian:**
```bash
# Python 3.12+
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip

# PostgreSQL 16+
sudo apt install postgresql postgresql-contrib

# Redis
sudo apt install redis-server

# Node.js (for docx tools)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs
```

**On macOS:**
```bash
# Install Homebrew if not already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 3.12+
brew install python@3.12

# PostgreSQL 16+
brew install postgresql@16
brew services start postgresql@16

# Redis
brew install redis
brew services start redis

# Node.js
brew install node
```

**On Windows:**
Download installers:
- Python: https://www.python.org/downloads/
- PostgreSQL: https://www.postgresql.org/download/windows/
- Redis: https://github.com/microsoftarchive/redis/releases
- Node.js: https://nodejs.org/

### Step 2: Create Project (5 minutes)

```bash
# Create project directory
mkdir campus_platform
cd campus_platform

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Create requirements file
cat > requirements.txt << EOF
Django==5.0
psycopg2-binary==2.9.9
celery==5.3.4
redis==5.0.1
python-dotenv==1.0.0
pytest==7.4.3
pytest-django==4.7.0
black==23.12.0
flake8==6.1.0
EOF

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Initialize Django (10 minutes)

```bash
# Start Django project
django-admin startproject config .

# Create kernel app
python manage.py startapp kernel

# Create folder structure
mkdir -p kernel/{models,services,middleware,repositories,tests,templates/kernel}
mkdir -p modules
mkdir -p config/settings

# Create __init__.py files
touch kernel/models/__init__.py
touch kernel/services/__init__.py
touch kernel/middleware/__init__.py
touch kernel/repositories/__init__.py
touch kernel/tests/__init__.py
```

### Step 4: Configure Database (5 minutes)

```bash
# Create PostgreSQL database
createdb campus_platform_dev

# Update config/settings.py
cat >> config/settings.py << EOF

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'campus_platform_dev',
        'USER': 'postgres',  # Change if needed
        'PASSWORD': '',      # Add your password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

INSTALLED_APPS += ['kernel']
EOF
```

---

## 🎯 Your First Task (Next 30 Minutes)

### Task 0.1.1: Create Person Model

Open `kernel/models/person.py` and paste this:

```python
import uuid
from django.db import models

class Person(models.Model):
    """
    Represents a real human being in the system.
    
    Immutable identity - one person exists across entire college installation.
    
    Constitution Reference: Section 2.1
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    full_name = models.CharField(max_length=200)
    
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Optional - used for age verification"
    )
    
    primary_email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        help_text="For contact, NOT authentication"
    )
    
    primary_phone = models.CharField(
        max_length=20,
        unique=True,
        help_text="Primary contact number"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    is_active = models.BooleanField(
        default=True,
        help_text="False = person has left institution"
    )
    
    class Meta:
        db_table = 'kernel_persons'
        indexes = [
            models.Index(fields=['primary_email']),
            models.Index(fields=['primary_phone']),
        ]
        verbose_name = 'Person'
        verbose_name_plural = 'Persons'
    
    def __str__(self):
        return self.full_name
```

Update `kernel/models/__init__.py`:
```python
from .person import Person

__all__ = ['Person']
```

Run migrations:
```bash
python manage.py makemigrations kernel --name add_person_model
python manage.py migrate
```

**CONGRATULATIONS!** 🎉 You just created your first model!

Now update the task list:

In `01_MASTER_TASK_LIST.md`, change:
```
- [ ] **1.1.1** Create `kernel/models/person.py`
```
to:
```
- [✓] **1.1.1** Create `kernel/models/person.py`
  - Status: Complete
  - Completion Date: 2025-02-12
  - Notes: Person model created with UUID primary key, indexes on email/phone
```

---

## 📋 What to Do Next

### Option A: Continue Building (Recommended)

Move to Task 1.1.2 in the Master Task List:
- Add indexes (already done in above code!)
- Move to Task 1.1.3: Model validation
- Then 1.1.4: Create migration

### Option B: Set Up Testing First

Create `kernel/tests/test_person.py`:
```python
import pytest
from kernel.models import Person

@pytest.mark.django_db
def test_create_person():
    person = Person.objects.create(
        full_name="Ahmed Khan",
        primary_email="ahmed@test.com",
        primary_phone="+92-300-1234567"
    )
    
    assert person.id is not None
    assert person.full_name == "Ahmed Khan"
    assert person.is_active == True

@pytest.mark.django_db
def test_person_string_representation():
    person = Person.objects.create(
        full_name="Sara Ali",
        primary_phone="+92-300-9876543"
    )
    
    assert str(person) == "Sara Ali"
```

Run tests:
```bash
pytest kernel/tests/test_person.py -v
```

### Option C: Set Up Admin Interface

Update `kernel/admin.py`:
```python
from django.contrib import admin
from kernel.models import Person

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'primary_email', 'primary_phone', 'is_active', 'created_at')
    search_fields = ('full_name', 'primary_email', 'primary_phone')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
```

Create superuser:
```bash
python manage.py createsuperuser
```

Run server and check admin:
```bash
python manage.py runserver
# Visit: http://localhost:8000/admin
```

---

## 🔄 The Daily Workflow

### Morning (15 minutes)
1. Open `01_MASTER_TASK_LIST.md`
2. Find first unchecked task
3. Read relevant Constitution section
4. Plan implementation

### Development (4-6 hours)
5. Write code following Constitution
6. Write tests
7. Run tests (must pass)
8. Update task list

### End of Day (15 minutes)
9. Commit with proper message: `[Phase 1] Task 1.1.1: Create Person model with UUID primary key`
10. Update flowchart if phase complete
11. Review progress

### Weekly
- Review completed tasks
- Update friends on progress
- Adjust timeline if needed

---

## 🎓 Learning Resources

### Django Essentials
- Official Django Tutorial: https://docs.djangoproject.com/en/5.0/intro/tutorial01/
- Django Models: https://docs.djangoproject.com/en/5.0/topics/db/models/
- Django Testing: https://docs.djangoproject.com/en/5.0/topics/testing/

### PostgreSQL
- PostgreSQL Tutorial: https://www.postgresqltutorial.com/
- Django + PostgreSQL: https://docs.djangoproject.com/en/5.0/ref/databases/#postgresql-notes

### Testing
- pytest-django: https://pytest-django.readthedocs.io/
- Django Testing Best Practices: https://realpython.com/testing-in-django-part-1-best-practices-and-examples/

---

## 🚨 When Things Go Wrong

### "I'm stuck on a task"
1. Check Constitution for relevant section
2. Check Prompt Pack for examples
3. Search similar code in Django docs
4. Ask for help (don't guess!)

### "Tests are failing"
1. Read error message carefully
2. Check if database is running: `pg_isready`
3. Run migrations: `python manage.py migrate`
4. Check test database permissions

### "I broke something"
1. Don't panic
2. Read error message
3. Git reset to last working commit: `git reset --hard HEAD~1`
4. Try again, one step at a time

---

## 📊 Progress Milestones

### After 1 Week (Phase 0 + 1)
- ✅ Environment set up
- ✅ Django project initialized
- ✅ All 8 core models created
- ✅ Migrations run successfully
- ✅ Admin interface working
- ✅ Sample data loaded

### After 2 Weeks (Phase 2)
- ✅ All services implemented
- ✅ Authorization engine working
- ✅ 90%+ test coverage
- ✅ Can create users and assign roles

### After 3 Weeks (Phase 3)
- ✅ Campus context middleware functional
- ✅ Context picker UI working
- ✅ Campus isolation verified (no data leaks)
- ✅ Dashboard accessible

### After 1 Month
- ✅ Audit logging complete
- ✅ Ready to start biometric integration

---

## 🎯 Success Metrics

**Track These Weekly:**

1. **Tasks Completed:** X of 120 (target: 15-20 per week)
2. **Test Coverage:** Y% (target: 90%+)
3. **Constitution Violations:** Z (target: 0)
4. **Lines of Code:** ~500-1000 per week (quality over quantity)

**Quality Over Speed:**
- One well-tested feature > Five broken features
- Zero violations > Fast progress
- Understanding > Copying code

---

## 💡 Pro Tips

### Use Git Branches
```bash
git checkout -b phase1-person-model
# Work on feature
git commit -m "[Phase 1] Task 1.1.1: Create Person model"
git checkout main
git merge phase1-person-model
```

### Use Django Shell for Quick Tests
```bash
python manage.py shell

>>> from kernel.models import Person
>>> p = Person.objects.create(full_name="Test User", primary_phone="+92-300-0000000")
>>> print(p.id, p.full_name)
```

### Use Black for Auto-Formatting
```bash
black kernel/
# Automatically formats all Python files
```

### Use VS Code Tasks
Create `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "pytest kernel/tests/ -v"
    },
    {
      "label": "Run Server",
      "type": "shell",
      "command": "python manage.py runserver"
    }
  ]
}
```

---

## 🎊 Celebrate Small Wins

- ✅ First model created? **Celebrate!**
- ✅ First test passing? **Celebrate!**
- ✅ First phase complete? **Celebrate!**
- ✅ Campus isolation working? **CELEBRATE!**

Building complex systems is hard. Acknowledge progress.

---

## 📞 Get Help

### Stuck? Blocked? Confused?

1. **Re-read Constitution** - Answer is probably there
2. **Check Prompt Pack** - Examples for common patterns
3. **Search Django docs** - Official documentation is excellent
4. **Ask in comments** - Document your question for future reference
5. **Take a break** - Sometimes you need fresh eyes

---

## 🚀 Final Pep Talk

You have:
- ✅ A world-class architecture (validated by 2 technical advisors)
- ✅ Complete documentation (25,000+ words)
- ✅ Detailed task breakdown (120+ actionable items)
- ✅ AI agent guidance (rules and examples)
- ✅ The skills to build this (proven with BACT portal)

**The only thing between you and a production system is execution.**

**Start with Task 0.1.1. Then 0.1.2. Then 0.1.3.**

**One task at a time. One day at a time.**

**7 weeks from now, you'll have a world-class identity system.**

**But it starts TODAY.**

---

## ✅ Your Checklist for Today

- [ ] Read this Quick Start Guide (you're doing it!)
- [ ] Install prerequisites (Python, PostgreSQL, Redis, Node.js)
- [ ] Create project directory and virtual environment
- [ ] Initialize Django project
- [ ] Create Person model (first task!)
- [ ] Run migrations
- [ ] Update task list
- [ ] Commit to Git
- [ ] Plan tomorrow's tasks

**Now go build something amazing.** 🚀

---

**P.S.** When you complete your first task, take a screenshot. You'll want to remember this moment when you're deploying to 100 colleges in 2 years.

**P.P.S.** The hardest part is starting. You just did that. Everything else is just following the Constitution, one task at a time.

**NOW GO!** ⚡
