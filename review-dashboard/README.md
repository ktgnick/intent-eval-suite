# Intent Review Dashboard

A dashboard for reviewing an intent classifier's predictions against gold-labeled messages. It shows accuracy per run, filterable prediction tables, a confusion matrix, and breakdowns by language and intent.

- **Front end:** Angular 16 with Angular Material, served as static files from S3.
- **API:** Spring Boot 4 (Java 21) with JDBC and read-only SQL over a `scored` view.
- **Database:** H2 in memory, with the schema and seed data managed by Liquibase.
- **Tests:** JUnit for the data layer, Playwright for end-to-end checks in a real browser.
- **CI:** GitHub Actions runs the API tests, the browser tests, and a dependency audit. Deploy runs on `main` once enabled.

The data comes from two earlier projects, [LLMeval](https://github.com/ktgnick/LLMeval) (gold set and baseline models) and [intent-api](https://github.com/ktgnick/intent-api) (the Claude classifier).

## Layout

```
api/                 Spring Boot API, Liquibase changelog, seed data, tests, Dockerfile
web/                 Angular 16 app and Playwright tests
scripts/build_seed.py  Rebuilds the seed CSVs from the two source projects
.github/workflows/ci.yml
render.yaml          Render config for the API (Docker)
```

## Run locally

Start the API (port 8080):

```bash
cd api
./mvnw spring-boot:run
```

Start the web app (port 4200) in another terminal:

```bash
cd web
npm install
npm start
```

Open http://localhost:4200.

## Tests

```bash
cd api && ./mvnw test          # checks the seeded numbers against the recorded results
cd web && npx playwright test  # starts both servers and runs the browser tests
```

## Rebuild the data

After changing results in either source project:

```bash
python3 scripts/build_seed.py ../LLMeval ../intent-api
```

A run whose prediction file contains error rows is skipped, so a failed API call never shows up as a wrong answer.

## API

| Endpoint | Returns |
|---|---|
| `GET /api/runs` | Each run with total, correct, and accuracy |
| `GET /api/runs/{id}/predictions?set=&language=&errorsOnly=` | Predictions with gold label and reason |
| `GET /api/runs/{id}/confusion?set=` | Gold × predicted counts |
| `GET /api/runs/{id}/breakdown?by=language\|intent&set=` | Accuracy per language or per gold intent |

Filter values are checked against a fixed list, and all values reach SQL as bound parameters.

## Deploy

1. **API on Render.** Create a Blueprint from this repo. It builds `api/Dockerfile`. Set `APP_CORS_ALLOWED_ORIGINS` to the S3 site URL.
2. **Front end URL.** Put the Render URL into `web/src/environments/environment.prod.ts` as `apiUrl`, ending in `/api`.
3. **S3 site.** Create a bucket with static website hosting, and allow public read on its objects.
4. **CI deploy.** In GitHub, set the variable `DEPLOY_ENABLED` to `true`, the variables `AWS_REGION` and `S3_BUCKET`, and the secret `AWS_ROLE_ARN` for an IAM role that trusts GitHub OIDC and can write to the bucket.

The API runs on Render's free tier, which sleeps when idle. The first request after a quiet period can take 30–60 seconds.

## Notes

- The database is in memory, so it reloads from the seed files on every start. Changes made through the API are not kept.
- The held-out results were written after the rubric was. See the intent-api README for the caveats.
