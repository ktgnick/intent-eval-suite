# Intent Review Dashboard

A dashboard for reviewing an intent classifier's predictions against gold-labeled messages. It shows accuracy per run, filterable prediction tables, a confusion matrix, and breakdowns by language and intent.

- **Front end:** Angular 16 with Angular Material, published to GitHub Pages. It has a Results tab (this data) and a Try it tab (calls the live classifier).
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

The live site is `https://ktgnick.github.io/intent-eval-suite/`. Set it up in this order.

1. **Review API on Render.** New > Web Service, pick `intent-eval-suite`, and set Runtime to **Docker**, Root Directory to `review-dashboard/api`, and Health Check Path to `/actuator/health`. Add the environment variable `APP_CORS_ALLOWED_ORIGINS` with the value `https://ktgnick.github.io`. Note the service URL Render gives you. (`render.yaml` in this folder is written for a repo whose root is this folder, so Render's form is simpler here.)
2. **Classifier on Render.** Open the existing `intent-api` service and point it at this repo with Root Directory `intent-api`. Set `ALLOWED_ORIGINS` to `https://ktgnick.github.io`. Keep `ANTHROPIC_API_KEY` set. Note its URL.
3. **Front end URLs.** In `web/src/environments/environment.prod.ts`, set `apiUrl` to the review API URL plus `/api`, and `classifierUrl` to the classifier URL. Commit and push.
4. **GitHub Pages.** In the repo settings, open Pages and set Source to **GitHub Actions**.
5. **Turn on deploy.** In the repo settings, under Variables, add `DEPLOY_ENABLED` with the value `true`. The deploy job then builds with base path `/intent-eval-suite/` and publishes to Pages.

The API runs on Render's free tier, which sleeps when idle. The first request after a quiet period can take 30–60 seconds.

## Notes

- The database is in memory, so it reloads from the seed files on every start. Changes made through the API are not kept.
- The held-out results were written after the rubric was. See the intent-api README for the caveats.
