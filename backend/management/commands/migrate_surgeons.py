# from django.core.management.base import BaseCommand
# from backend.models import Surgery, SurgerySurgeon

# class Command(BaseCommand):
#     help = "Migrates existing ManyToManyField data to the new through model"

#     def handle(self, *args, **kwargs):
#         for surgery in Surgery.objects.all():
#             surgeons = surgery.surgeons1.all()
#             for index, surgeon in enumerate(surgeons):
#                 print(surgeon)
#                 SurgerySurgeon.objects.create(surgery=surgery, surgeon=surgeon, sequence=index)
        
#         self.stdout.write(self.style.SUCCESS('Successfully migrated surgeons data!'))
