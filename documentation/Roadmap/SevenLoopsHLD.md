# Seven Loops HLD

## Goal
Build the agent as seven loop contracts. Each loop keeps asking, testing, or rebuilding until its exit artifact is safe for the next loop. The count is not sacred; seven is the current cut because it maps to the decisions a sales head must trust before acting.

## Loop 1: Context Loop
Purpose: capture the sales action before touching modeling.

Done when the system knows:
- who will act on the output
- what action they will take
- which customer entity must be ranked
- how many customers the team can handle
- which columns the action file must contain
- what churn or risk means to the user
- what evidence would make the user trust the output

Exit artifact: Action Context Brief.

Failure behavior: ask the next missing question. Do not train. Do not infer target. Do not invent context.

## Loop 2: Data Understanding Loop
Purpose: explain what data exists in business terms.

Done when the user agrees that the files, joins, grain, customer identifiers, date columns, product columns, amount columns, geography, and owner columns are understood.

Exit artifact: Data Reality Brief.

Failure behavior: ask for file meaning, column meaning, or grain correction.

## Loop 3: Data Readiness Loop
Purpose: decide whether the available data can support the action.

Done when the data has enough customer history, time coverage, customer identifiers, transaction dates, value measures, and fields needed for the requested action file.

Exit artifact: Readiness Report with blockers, warnings, and safe scope.

Failure behavior: shrink the scope, ask for more data, or mark the output as advisory.

## Loop 4: Risk Definition Loop
Purpose: turn business risk into measurable labels or proxies.

Done when the churn window, observation window, loss definition, dormant definition, and exclusion rules match the user's business process.

Exit artifact: Risk Definition Contract.

Failure behavior: show candidate definitions and ask which loss pattern matches the business.

## Loop 5: Signal Loop
Purpose: build behavior signals that a sales manager can inspect.

Done when each signal has a business explanation, source columns, time window, and example customers that prove the signal is real.

Exit artifact: Signal Ledger.

Failure behavior: drop signals that cannot be traced to the user's data or explained in sales terms.

## Loop 6: Validation Loop
Purpose: prove the model against history in a way the user can verify.

Done when the model identifies known lost customers, explains misses, and beats simple rules on the user's history.

Exit artifact: Trust Report.

Failure behavior: rebuild labels, signals, or scope until the report is useful, or stop with a no-go.

## Loop 7: Action Output Loop
Purpose: produce a file the field team can use.

Done when the output has customer names, risk level, behavior changes, owner fields, priority, suggested action, and caveats.

Exit artifact: Field Action File.

Failure behavior: reshape the file to the actor, territory, capacity, and columns from Loop 1.

## First Implementation Scope
Implement Loop 1 only.

The first loop is deterministic. It receives whatever context exists and returns one of two states:
- not done: next missing question plus current answers
- done: Action Context Brief

It must not infer modeling choices. It must not start the pipeline. Its job is to protect the rest of the system from acting before the user's job-to-be-done is known.
