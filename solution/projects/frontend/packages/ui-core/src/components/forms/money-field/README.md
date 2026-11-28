# MoneyField

An amount input that formats as you type and reports **minor units** — cents,
not dollars.

```tsx
const [price, setPrice] = useState(1999);   // $19.99

<MoneyField currency="USD" value={price} onValueChange={setPrice} />
```

## The value is an integer

`value` and `onValueChange` carry minor units. A field that hands back `19.99`
hands back a number that does not exist in binary floating point: totals drift
by a cent, and the bug surfaces in an invoice rather than in a test. `1999` is
exact.

This matches `@djangocfg/payments`, which moves `MinorUnits` for the same
reason — a value goes from this field to a charge with no conversion between.

## Entry is till-style

Digits fill from the right: `1` `9` `9` reads $1.99. The caret never has to sit
"before the decimal point", which is the state that makes most currency inputs
confusing.

Every keystroke rewrites the whole display, so the caret is restored by **digit
count, not string offset**. Inserting a thousands separator shifts every
character after it, and an offset-based restore moves the caret a place — the
single most common defect in a currency input.

## Separators come from `Intl`

The decimal mark is a comma across most of Europe. Guessing it means `1.234` is
read as either 1.234 or 1234 depending on the user, with nothing on screen to
say which happened. Pass `locale` to pin it; otherwise the runtime's is used.

## Zero-decimal currencies

¥500 is five hundred yen, not five. `currencyFractionDigits()` and
`minorUnitFactor()` are exported for callers that need the same rule:

```ts
minorUnitFactor('USD')          // 100
minorUnitFactor('JPY')          // 1
currencyFractionDigits('JPY')   // 0
```

The zero-decimal list mirrors `@djangocfg/payments`' `domain/money.ts`. It is
duplicated rather than imported because `ui-core` sits **below** `payments` in
the dependency direction and may not depend on it.

## Props

| Prop | Type | Notes |
|---|---|---|
| `value` | `number` | Amount in minor units (controlled). |
| `defaultValue` | `number` | Uncontrolled initial amount, minor units. |
| `onValueChange` | `(minorUnits: number) => void` | |
| `currency` | `string` | ISO 4217. Drives symbol, decimals, minor-unit factor. Default `USD`. |
| `fractionDigits` | `number` | Overrides the currency's decimals. `0` makes the field whole-unit — see below. |
| `locale` | `string` | BCP 47. Defaults to the runtime's. |
| `showSymbol` | `boolean` | Default `true`. Set false when the label carries the unit. |
| `max` | `number` | Minor units. Entry beyond it is ignored, not clamped after the fact. |
| `groupClassName` | `string` | Applied to the group, to size the whole control. |

## Whole amounts

The default suits money that is paid — a price, an invoice, a charge. It does
not suit money that is merely large. On a property asking price the cents are
two zeros the reader looks past and, because entry is right-anchored, two
keystrokes they have to type: 1,400,000 costs nine digits, not seven.

`fractionDigits={0}` makes the field whole-unit:

```tsx
const [asking, setAsking] = useState(1_400_000);   // dollars, not cents

<MoneyField currency="USD" fractionDigits={0} value={asking} onValueChange={setAsking} />
// shows "1,400,000"; typing 1400000 reads as 1,400,000
```

**The unit of `value` follows this prop.** Minor units at the default, major
units at `0` — the component divides by `10 ** fractionDigits`, so a caller
that changes the prop must change what it stores. This is deliberate: an
integer at any precision keeps the exactness the component exists for, and a
field that reported cents while displaying whole dollars would be a trap.

## Accessibility

The currency symbol is `aria-hidden` — a screen reader announcing "dollar sign"
on entry is noise. The accessible name has to come from a label you associate
yourself:

```tsx
<label htmlFor={id}>Price</label>
<MoneyField id={id} … />
```

Text is left-aligned so it hugs the symbol. Right alignment belongs to a column
of amounts in a table; pass `className="text-right"` there.
