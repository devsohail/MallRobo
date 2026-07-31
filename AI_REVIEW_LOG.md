# AI Review Log

This document tracks instances where AI-generated code was corrected during development.

| # | Date | What Was Wrong | How Found | Fix Applied |
|---|------|---------------|-----------|-------------|
| 1 | 2026-07-31 | `product.price` treated as `number` but API returns it as `string` (Decimal serialization). Caused `TypeError: price.toFixed is not a function` in `ProductList.tsx` and `Cart.tsx`. | User reported runtime crash when selecting a store and adding products to cart. | Wrapped all `price` usages with `Number()` before calling `.toFixed(2)` or arithmetic in `ProductList.tsx:43` and `Cart.tsx:15,29`. |
