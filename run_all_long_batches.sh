#!/bin/bash
# Master script to process all 400 symbols in batches of 10
# Each batch runs as separate process, freeing memory between runs

echo "================================================================================"
echo "PROCESSING ALL LONG SIGNALS IN 40 BATCHES (10 symbols each)"
echo "================================================================================"

BATCH_SIZE=5
TOTAL_SYMBOLS=400
TOTAL_BATCHES=$((TOTAL_SYMBOLS / BATCH_SIZE))

for ((batch=0; batch<TOTAL_BATCHES; batch++)); do
    START_IDX=$((batch * BATCH_SIZE))
    END_IDX=$(((batch + 1) * BATCH_SIZE))
    
    echo ""
    echo "--------------------------------------------------------------------------------"
    echo "BATCH $((batch + 1))/$TOTAL_BATCHES: Processing symbols $START_IDX to $((END_IDX - 1))"
    echo "--------------------------------------------------------------------------------"
    
    # Run batch (process exits and frees memory when done)
    python3.11 /home/ubuntu/stage4_optimization/process_best_long_subset.py $START_IDX $END_IDX
    
    # Check if batch succeeded
    if [ $? -eq 0 ]; then
        echo "✓ Batch $((batch + 1)) completed successfully"
    else
        echo "✗ Batch $((batch + 1)) FAILED"
        exit 1
    fi
    
    # Small pause to ensure memory is freed
    sleep 2
done

echo ""
echo "================================================================================"
echo "ALL BATCHES COMPLETE - Now combining results..."
echo "================================================================================"

# Combine all batch files
python3.11 /home/ubuntu/stage4_optimization/combine_long_batches.py

echo ""
echo "================================================================================"
echo "✓ PROCESSING COMPLETE!"
echo "================================================================================"
