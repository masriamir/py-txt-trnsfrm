web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -
release: python -c "print('Release phase: Application ready for deployment')"
