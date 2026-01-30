from udata.models import Dataset
from udata.app import create_app
import sys


def migrate():
    print("Starting migration check...")
    app = create_app()
    with app.app_context():
        # Find datasets that have the old extras structure
        # We look for datasets where extras.harvest:remote_id exists
        # Note: MongoEngine syntax for checking key existence in DictField can be tricky,
        # but usually checking generic existence or iterating is fine for a script.
        # We can use a raw query for efficiency.

        # Step 1: Identify "Good" datasets (already have harvest info correctly set)
        print("Identifying already valid, correct datasets...")
        good_datasets = {}  # remote_id -> dataset_id

        # We need to iterate carefully.
        # Dataset.objects(harvest__exists=True) might be too broad if we have other harvesters.
        # But for INE, we know the source/remote_idea logic.
        # Let's iterate ALL datasets that have a harvest.remote_id

        # Note: In MongoEngine, we can filter for embedded fields
        valid_ds_qs = Dataset.objects(harvest__remote_id__exists=True)
        for ds in valid_ds_qs:
            if ds.harvest and ds.harvest.remote_id:
                good_datasets[ds.harvest.remote_id] = ds.id

        print(f"Found {len(good_datasets)} already valid datasets.")

        # Step 2: Iterate "Bad" datasets (legacy extras)
        qs = Dataset.objects(__raw__={"extras.harvest:remote_id": {"$exists": True}})
        total_legacy = qs.count()
        print(f"Found {total_legacy} datasets with legacy extras info.")

        if total_legacy == 0:
            print("No legacy datasets to migrate.")
            return

        migrated = 0
        deleted = 0
        errors = 0
        seen_legacy_rids = set()  # To track duplicates within the legacy batch

        print("Starting deduplication and migration...")

        # We iterate and process
        # Since we might delete, we should probably be careful about the cursor, but typical mongo iter is okay
        # unless we are deleting the CURRENT document, which we are.
        # Safest is to fetch ID and basic info first, then process one by one?
        # Or just iterate the cursor.

        count = 0
        for ds in qs:
            count += 1
            if count % 100 == 0:
                print(f"Processed {count}/{total_legacy} legacy entries...")

            try:
                remote_id = ds.extras.get("harvest:remote_id")

                if not remote_id:
                    continue

                # Case 1: We already have a GOOD dataset for this remote_id
                if remote_id in good_datasets:
                    # check if it is the SAME dataset (just redundant info in extras? unlikely but possible)
                    if good_datasets[remote_id] == ds.id:
                        # It's the same object! Just clean up the extras
                        ds.extras.pop("harvest:remote_id", None)
                        ds.extras.pop("harvest:source_id", None)
                        ds.extras.pop("harvest:domain", None)
                        ds.extras.pop("harvest:last_update", None)
                        ds.save()
                        migrated += 1
                        # print(f"Cleaned up extras for existing valid dataset {ds.id}")
                    else:
                        # It is a distinct duplicate of a good dataset. Delete it.
                        ds.delete()
                        deleted += 1
                        # print(f"Deleted duplicate legacy dataset {ds.id} for remote_id {remote_id}")
                    continue

                # Case 2: We have seen this remote_id in this legacy batch already
                if remote_id in seen_legacy_rids:
                    # It's a duplicate of a legacy dataset we just decided to keep/migrate. Delete this one.
                    ds.delete()
                    deleted += 1
                    continue

                # Case 3: New unique legacy dataset. Migrate it.
                if not ds.harvest:
                    ds.harvest = Dataset.harvest.document_type_obj()

                ds.harvest.remote_id = remote_id

                sid = ds.extras.get("harvest:source_id")
                dom = ds.extras.get("harvest:domain")

                if sid:
                    ds.harvest.source_id = sid
                if dom:
                    ds.harvest.domain = dom

                # Cleanup extras
                ds.extras.pop("harvest:remote_id", None)
                ds.extras.pop("harvest:source_id", None)
                ds.extras.pop("harvest:domain", None)
                ds.extras.pop("harvest:last_update", None)

                ds.save()

                # Register as "good" now
                good_datasets[remote_id] = ds.id
                seen_legacy_rids.add(remote_id)
                migrated += 1

            except Exception as e:
                print(f"Error processing dataset {ds.id}: {e}")
                errors += 1

        print(f"Migration finished.")
        print(f"Migrated/Cleaned: {migrated}")
        print(f"Deleted Duplicates: {deleted}")
        print(f"Errors: {errors}")


if __name__ == "__main__":
    migrate()
