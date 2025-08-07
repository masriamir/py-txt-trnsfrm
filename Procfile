web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - --log-level info
release: python -c "print('Release phase: Application ready for deployment')"
