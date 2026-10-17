# Labeling rubric: customer message intent

Each message gets exactly one label, or `ambiguous`.'ambiguous` messages are excluded from accuracy and kappa, listed in a separate review file.

## Intents

### order_status
- **Definition:** The customer asks about the shipping or delivery of an order.
- **Includes:** shipping information, delivery information, "where is my package," "has it shipped yet"
- **Excludes:** any message that asks to cancel (see tie-break 1)

### cancel_order
- **Definition:** The customer wants an order or subscription stopped.
- **Includes:** canceling an order, cancelling a subscription, cancelling an order placed by mistake, refund on an order that has not shipped yet
- **Excludes:** refunds on orders already delivered or returned

### refund_request
- **Definition:** The customer wants money back.
- **Includes:** refund for a whole order, partial refund, refund for a return, damaged or missing item, double charge
- **Excludes:** refund on an order that has not shipped yet (use `cancel_order`)

## Tie-break rules

1. If the message asks to cancel and also asks for status, label `cancel_order`.
2. If the order has not shipped, a request for money back is `cancel_order`. If the order has shipped, delivered, or been returned, it is `refund_request`.

## Escalation

If a message still fits two labels equally after the rules above, label it `ambiguous`, add a short review note saying which two labels it fits, and send it for human review. Do not force a label.

If the message describes receiving an order (arrived, missing item, damaged), treat it as shipped.”

