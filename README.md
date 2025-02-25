# SUBHUB

Winner of Stripe track HackIreland 2025 
Link to devpost and tutorial -> https://devpost.com/software/team3-subhub

# Inspiration
Modern life comes with endless subscriptions, but managing them shouldn’t be a chore. From splitting bills with roommates to forgetting payment dates or overpaying for services you barely use, subscription fatigue is real. Traditional solutions leave you drowning in spreadsheets, calendar alerts, and guesswork—costing you time, money, and peace of mind.

# What it does
Gain instant visibility into every subscription, payment date, and cost. No more surprises—see your entire financial landscape at a glance.

Smart Cost Splitting- Share subscriptions effortlessly with customizable virtual payment cards. Split Netflix with roommates, Spotify with friends, or SaaS tools with coworkers—set rules for who pays what, and let the platform handle the rest.

Spending Insights & Alerts- Track trends, identify unused services, and get proactive reminders before payments hit. Never miss a renewal—or waste money on subscriptions you’ve outgrown.

Cost-Saving Recommendations- Discover cheaper alternatives tailored to your needs. Our algorithm analyzes your usage and suggests better deals, free trials, or bundled offers—so you always get the best value.

Security- Manage shared payments risk-free with encrypted virtual cards and role-based access. Your data stays private, and your transactions stay secure.

# How we built it
Our backend is built with Python, using FastAPI to handle APIs quiries. On the frontend, we use React to interact with these APIs. For styling, we reply on Tailwind CSS and ShadCN. We use the Stripe api to create virtual cards and add payment and subscription splitting functionality. Our demo setup runs on Flask, to simulate a real world scenario.

# Challenges we ran into
versions of tailwind conflicting
ideation
endless problems with packages
Post-celcius sleep
Issues with StripeAPI
taiilwind issues
versioning isssues
.env files not being recognised
Accomplishments that we're proud of
Designing a full stack website within 30 hours - that is applicable to the real world.
We allow users to upload statements of their subscription payments and we automatically create insights around our analysis. -Networking with others
What we learned
We faced issues with version conflicts, package dependencies, and environment variables. This taught us the importance of version control and proper documentation. The importance of logging in code. How to delegate taks to others
