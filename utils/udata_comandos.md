# Documentação dos Comandos uData

---

## udata
**`Usage: udata [OPTIONS] COMMAND [ARGS]...`**
  udata management client

**`Options:`**
* --version
* **`-?,`** - -h, --help  Show this message and exit.

**`Commands:`**
* **`api`** - API related operations
* **`badges`** - Badges related operations
* **`cache`** - Cache related operations.
* **`collect`** - Collect static files
* **`dataset`** - Dataset related operations
* **`db`** - Database related operations
* **`dcat`** - DCAT diagnosis operations
* **`frequency-reminder`** - Send a unique email per organization to members
* **`generate-fixtures-file`** - Build sample fixture file based on datasets...
* **`harvest`** - Remote repositories harvesting operations
* **`images`** - Images related operations
* **`import-fixtures`** - Build sample fixture data (users, datasets,...
* **`info`** - Display some details about the local environment
* **`init`** - Initialize your udata instance (search index,...
* **`job`** - Jobs related operations
* **`licenses`** - Feed the licenses from a JSON file
* **`linkchecker`** - Link checking operations
* **`metrics`** - Metrics related operations
* **`organizations`** - Organizations related operations
* **`purge`** - Permanently remove data flagged as deleted.
* **`roles`** - Role commands.
* **`search`** - Search/Indexation related operations
* **`serve`** - Runs a development server.
* **`shell`** - Run a shell in the app context.
* **`sitemap`** - Generate static sitemap to given directory.
* **`spatial`** - Geospatial related operations
* **`test`** - Some commands for testing purpose
* **`user`** - User related operations
* **`users`** - User commands.
* **`worker`** - Worker related operations

---

## udata api
**`Usage: udata api [OPTIONS] COMMAND [ARGS]...`**
  API related operations

**`Options:`**
* **`-?,`** - -h, --help  Show this message and exit.

**`Commands:`**
* **`create-oauth-client`** - Creates an OAuth2Client instance in DB
* **`postman`** - Dump the API as a Postman collection
* **`swagger`** - Dump the swagger specifications
* **`validate`** - Validate the Swagger/OpenAPI specification with...

---

## udata badges
**`Usage: udata badges [OPTIONS] COMMAND [ARGS]...`**
  Badges related operations

**`Options:`**
* **`-?,`** - -h, --help  Show this message and exit.

**`Commands:`**
* **`toggle`** - Toggle a `badge_kind` for a given `path_or_id`

---

## udata cache
**`Usage: udata cache [OPTIONS] COMMAND [ARGS]...`**
  Cache related operations.

**`Options:`**
* **`-?,`** - -h, --help  Show this message and exit.

**`Commands:`**
* **`flush`** - Flush the cache

---

## udata collect
**`Usage: udata collect [OPTIONS] [PATH]`**
  Collect static files

**`Options:`**
* **`-ni,`** - --no-input  Disable input prompts
* **`-?,`** - -h, --help   Show this message and exit.

---

## udata dataset
**`Usage: udata dataset [OPTIONS] COMMAND [ARGS]...`**
  Dataset related operations

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* **`archive`** - Archive multiple datasets from a list in a file (one id...
* **`archive-one`** - Archive one dataset

---

## udata db
**`Usage: udata db [OPTIONS] COMMAND [ARGS]...`**
  Database related operations

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* check-duplicate-resources-ids
* **`check-integrity`** - Check the integrity of the database from...
* **`info`** - Display detailed info about a migration
* **`migrate`** - Perform database migrations
* **`status`** - Display the database migrations status
* **`unrecord`** - Remove a database migration record.

---

## udata dcat
**`Usage: udata dcat [OPTIONS] COMMAND [ARGS]...`**
  DCAT diagnosis operations

**`Options:`**
* **`-?,`** - -h, --help  Show this message and exit.

**`Commands:`**
* **`parse-url`** - Parse the datasets in a DCAT format located at URL (debug)

---

## udata harvest
**`Usage: udata harvest [OPTIONS] COMMAND [ARGS]...`**
  Remote repositories harvesting operations

**`Options:`**
* **`-?,`** - -h, --help  Show this message and exit.

**`Commands:`**
* **`attach`** - Attach existing datasets to their harvest remote id
* **`backends`** - List available backends
* **`clean`** - Delete all datasets linked to a harvest source
* **`create`** - Create a new harvest source
* **`delete`** - Delete a harvest source
* **`launch`** - Launch a source harvesting on the workers
* **`purge`** - Permanently remove deleted harvest sources
* **`run`** - Run a harvester synchronously
* **`schedule`** - Schedule a harvest job to run periodically
* **`sources`** - List all harvest sources
* **`unschedule`** - Unschedule a periodical harvest job
* **`validate`** - Validate a source given its identifier

---

## udata images
**`Usage: udata images [OPTIONS] COMMAND [ARGS]...`**
  Images related operations

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* **`render`** - Force (re)rendering stored images

---

## udata info
**`Usage: udata info [OPTIONS] COMMAND [ARGS]...`**
  Display some details about the local environment

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* **`config`** - Display some details about the local configuration
* **`plugins`** - Display some details about the local plugins

---

## udata init
**`Usage: udata init [OPTIONS]`**
  Initialize your udata instance (search index, user, sample data...)

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

---

## udata job
**`Usage: udata job [OPTIONS] COMMAND [ARGS]...`**
  Jobs related operations

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* **`list`** - List all availables jobs
* **`run`** - Run the job <name>
* **`schedule`** - Schedule the job <name> to run periodically given the...
* **`scheduled`** - List scheduled jobs.
* **`unschedule`** - Unschedule the job <name> with the given parameters.

---

## udata licenses
**`Usage: udata licenses [OPTIONS] [SOURCE]`**
  Feed the licenses from a JSON file

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

---

## udata linkchecker
**`Usage: udata linkchecker [OPTIONS] COMMAND [ARGS]...`**
  Link checking operations

**`Options:`**
* **`-?,`** - -h, --help  Show this message and exit.

**`Commands:`**
* **`check`** - Check <number> of URLs that have not been (recently) checked

---

## udata metrics
**`Usage: udata metrics [OPTIONS] COMMAND [ARGS]...`**
  Metrics related operations

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* **`update`** - Update all metrics for the current date

---

## udata organizations
**`Usage: udata organizations [OPTIONS] COMMAND [ARGS]...`**
  Organizations related operations

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* **`attach-zone`** - Attach a zone <geoid> restricted to level for a given...
* **`detach-zone`** - Detach the zone of a given <organization>.

---

## udata purge
**`Usage: udata purge [OPTIONS]`**
  Permanently remove data flagged as deleted.
  If no model flag is given, all models are purged.

**`Options:`**
* **`-d,`** - --datasets
* **`-r,`** - --reuses
* **`-o,`** - --organizations
* --dataservices
* **`-h,`** - -?, --help       Show this message and exit.

---

## udata roles
**`Usage: udata roles [OPTIONS] COMMAND [ARGS]...`**
  Role commands.

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* **`add`** - Add role to user.
* **`add_permissions`** - Add permissions to role.
* **`create`** - Create a role.
* **`remove`** - Remove role from user.
* **`remove_permissions`** - Remove permissions from role.

---

## udata search
**`Usage: udata search [OPTIONS] COMMAND [ARGS]...`**
  Search/Indexation related operations

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* **`index`** - Initialize or rebuild the search index

---

## udata serve
**`Usage: udata serve [OPTIONS]`**
  Runs a local udata development server.
  This local server is recommended for development purposes only but it can
  also be used for simple intranet deployments.
  By default it will not support any sort of concurrency at all to simplify
  debugging. This can be changed with the --with-threads option which will
  enable basic multithreading.
  The reloader and debugger are by default enabled if the debug flag of Flask
  is enabled and disabled otherwise.

**`Options:`**
* **`-h,`** - --host TEXT                 The interface to bind to.
* **`-p,`** - --port INTEGER              The port to bind to.
* **`-r,`** - --reload / -nr, --no-reload
* **`Enable`** - or disable the reloader.  By default
* **`the`** - reloader is active if debug is enabled.
* **`-d,`** - --debugger / -nd, --no-debugger
* **`Enable`** - or disable the debugger.  By default
* **`the`** - debugger is active if debug is enabled.
* **`--eager-loading`** - / --lazy-loader
* **`Enable`** - or disable eager loading.  By default
* **`eager`** - loading is enabled if the reloader is
* disabled.
* **`--with-threads`** - / --without-threads
* **`Enable`** - or disable multithreading.
* **`-?,`** - --help                      Show this message and exit.

---

## udata shell
**`Usage: udata shell [OPTIONS]`**
  Run an interactive Python shell in the context of a given Flask application.
  The application will populate the default namespace of this shell according
  to its configuration.
  This is useful for executing small snippets of management code without
  having to manually configure the application.

**`Options:`**
* **`-?,`** - -h, --help  Show this message and exit.

---

## udata sitemap
**`Usage: udata sitemap [OPTIONS]`**
  Generate static sitemap to given directory.

**`Options:`**
* **`-o,`** - --output-directory TEXT  Output directory for sitemap files.
* **`-v,`** - --verbose
* **`-h,`** - -?, --help               Show this message and exit.

---

## udata spatial
**`Usage: udata spatial [OPTIONS] COMMAND [ARGS]...`**
  Geospatial related operations

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* **`load`** - Load a geozones archive from <filename>
* **`migrate`** - Migrate zones from old to new ids in datasets.

---

## udata test
**`Usage: udata test [OPTIONS] COMMAND [ARGS]...`**
  Some commands for testing purpose

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* **`log`** - Test logging

---

## udata user
**`Usage: udata user [OPTIONS] COMMAND [ARGS]...`**
  User related operations

**`Options:`**
* **`-?,`** - -h, --help  Show this message and exit.

**`Commands:`**
* **`activate`** - Activate an existing user (validate their email...
* **`create`** - Create a new user
* **`delete`** - Delete an existing user
* password
* **`rotate-password`** - Ask user for password rotation on next login and reset...
* **`set-admin`** - Set an user as administrator

---

## udata users
**`Usage: udata users [OPTIONS] COMMAND [ARGS]...`**
  User commands.
  For commands that require a USER - pass in any identity attribute.

**`Options:`**
* **`-?,`** - -h, --help  Show this message and exit.

**`Commands:`**
* **`activate`** - Activate a user.
* **`change_password`** - Administratively change a user's password.
* **`create`** - Create a new user with one or more attributes using the
* **`syntax:`** - attr:value. If attr isn't set 'email' is presumed.
* **`Identity`** - attribute values will be validated using the
* **`configured`** - confirm_register_form; however, any ADDITIONAL
* **`attribute:value`** - pairs will be sent to datastore.create_user
* **`deactivate`** - Deactivate a user.
* **`reset_access`** - Reset all authentication credentials for user.

---

## udata worker
**`Usage: udata worker [OPTIONS] COMMAND [ARGS]...`**
  Worker related operations

**`Options:`**
* **`-h,`** - -?, --help  Show this message and exit.

**`Commands:`**
* **`start`** - Start a worker
* **`status`** - List queued tasks aggregated by name
* **`tasks`** - Display registered tasks with their queue
