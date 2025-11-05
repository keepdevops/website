#!/bin/bash

echo "🧪 Running SaaS Platform Tests..."
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing test dependencies..."
    pip install -r requirements.txt
fi

# Run tests with coverage
echo "Running unit tests..."
pytest tests/ -v --tb=short

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Exit code: $TEST_EXIT_CODE"
fi

exit $TEST_EXIT_CODE

