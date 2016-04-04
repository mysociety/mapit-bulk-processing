Mapit Bulk Processing
=====================

This repo contains a prototype Django app/project for performing self-service
mapit bulk lookups. Currently, users  supply a CSV file with a postcode column,
tell us which column that is, and then choose a selection of mapit areas to be
added to the file. Payment is taken via StripeThe file
is processed asynchronously via a cron job, and then an email is sent to the
user when it's finished.

Development
-----------
A Vagrantfile is included for an Ubuntu 14.04 virtual machine that should
provision itself correctly to start running the site. To start it, `cd` into
the directory you cloned this repo into and then run:

```
vagrant up && vagrant ssh
cd /vagrant/mapit-bulk-processing
source ../virtualenv-mapit-bulk-processing/bin/activate
python manage.py runserver 0.0.0.0:8000
```

You'll need to provide a Stripe key pair in `conf/general.yml-example` in
order to make the payment form work. After which you can use Stripe's test
card number `4242 4242 4242 4242` (with any future expiry date and numeric CVC)
to make payments.

You should now be able to access the site at http://localhost:8000 and a
mailcatcher inbox for the emails it sends at http://localhost:1080.

Finally, you need to create some options for the output columns, these are
currently specified as a simple name and then a mapit area type code
(e.g. `WMC`). The code can support any of the existing type codes in mapit in
this way.

TODO
----
- Lookups are currently processed via a management command that we can run
  from a cron job, but this won't scale to the types of lookups we've seen in
  the past (hundreds of thousands of postcodes). We need to replace this with
  some kind of job queue and worker daemon(s) setup.
  (https://github.com/ui/django-rq perhaps?)
- Uploaded and processed files are just stored in the media root and linked to
  directly. We need to make sure they're secured properly because they could
  contain data that the user doesn't want anyone else to see. It seems like
  the best option would be to generate a secure password at the last step that
  we ask the user to save (or we ask them to give one). We can then
  effectively create them a user account on the site and force them to login
  before handing over the data. (Something like this:
  http://blog.wearefarm.com/2015/02/09/contact-form-uploads/ should then work
  fine).
- Better range and error checking. We should probably have a limit on the
  size of files (in MB and number of rows), and we could save a lot of
  problems later on if we can check that the postcodes they supply are
  actually real (or at least valid). (We have a library for that already: https://github.com/mysociety/uk-postcode-utils/blob/master/ukpostcodeutils/validation.py, but I'm not sure if it'll
  be fast enough to do big files on the fly.)
- Decide if this is going to be an app in the mapit.mysociety.org repo, or a
  standalone site. Currently it calls through to a Mapit api using requests,
  it could probably be a lot quicker if it could access the Mapit db directly,
  and we could potentially share login credentials/payment info with the new
  api key system, but it might also be more desirable to keep things separate.
- Tests + Health Checks!

Future Expansion
----------------
- Allow lat/lon or easting/northing fields in the CSV as well as postcodes
- Allow Excel files or JSON input as well as CSV
- Export to JSON or Excel instead of CSV
- More complicated output options (e.g. generations, ceremonial counties,
  choosing which codes or other info to extract for each output option)
- Performance enhancements such as rate-limiting ourselves with mapit calls,
  and limiting the area types we ask for in the call to mapit. Sharding big
  files, zip compression for input/output.
- Webhooks instead of email for results
- Progress updates/a status page for each job
- Better admin actions for re-running jobs/checking on their status
- Error reporting (e.g. x postcodes in this file weren't valid, here they are)
- Partial refunds for rows we couldn't process
