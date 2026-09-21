# Udatracker Starter Code

## Reflection

One design decision I made was to add more tests to `test_api.py` to cover additional paths. The instructions claimed that this file was complete, but for the most part it only covered the happy path.

One quirk I ran into was when trying to test a missing JSON body. I was going to include it in my bad request tests for the update and add routes. But without 'Content-Type: application/json' set, if there is no body to guess what the content type should be, a 415 is sent automatically. I caught this by checking `not request.data` so I could send an error message with the status code.

If I were continuing this project, my next step would be to support deleting orders, so the full CRUD is available. Switching from in-memory storage to SQL would be the logical next step.

## File structure

The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```