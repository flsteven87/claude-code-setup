# Naming Conventions

> Extracted from CLAUDE.md. These conventions apply across all projects.

## Class Naming 🟡

| Pattern       | Use When                        | Example                           |
| ------------- | ------------------------------- | --------------------------------- |
| **Handler**   | Stateful workflow orchestration | `PaymentHandler`, `UploadHandler` |
| **Processor** | Stateless data transformation   | `ImageProcessor`, `CSVProcessor`  |
| **Service**   | Business logic encapsulation    | `OrderService`, `AuthService`     |

## Files & Directories 🟡

| Type                 | Frontend                           | Backend         |
| -------------------- | ---------------------------------- | --------------- |
| Components           | `PascalCase.tsx`                   | -               |
| Hooks                | `useCamelCase.ts`                  | -               |
| Utilities/lib        | `kebab-case.ts`                    | `snake_case.py` |
| Directories          | `kebab-case/`                      | `snake_case/`   |
| shadcn/ui components | `lowercase.tsx` (their convention) | -               |

## Code Identifiers 🟡

| Element              | TypeScript        | Python            |
| -------------------- | ----------------- | ----------------- |
| Variables, functions | `camelCase`       | `snake_case`      |
| Classes, Components  | `PascalCase`      | `PascalCase`      |
| Constants            | `SCREAMING_SNAKE` | `SCREAMING_SNAKE` |
| Types, Interfaces    | `PascalCase`      | `PascalCase`      |
| Env variables        | `SCREAMING_SNAKE` | `SCREAMING_SNAKE` |
