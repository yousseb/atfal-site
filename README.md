# atfal-site (Reunite)

Data admin and tracking for Atfalmafkoda Facebook page to track cases. 
The main target is allowing classification of cases and photos in order to use the AI engine to enhance the 
images and allow us to implement face againg and face recognition in the hope of reuniting children (or in some cases adults) with their families.

## Components
1. Django Admin Site (Main web admin)
2. Celery Tasks (Facebook page harvesting using Apify)

## Deployment
We rely on Oracle's free tier offering. The application uses 

1. PostgreSQL database which we deploy to an instance. This service is started as a `systemd` service
2. docker-comompose-web: Starts the web admin components and dependencies on a single ARM instance
3. docker-componse-services: Starts the Celery task scheduler and Facebook importer - will later start the AI task scheduler. Lives on a single ARM instance. 
4. Atfal-ai lives in a stand-alone repository and will also live on a single instance
5. We rely on Oracle's object storage (S3 bucket compatible) for image storage.

   
## Debugging Live Servers
1. For web `docker compose -f docker-compose-web.yml logs`
2. For services `docker compose -f docker-compose-services.yml logs`
