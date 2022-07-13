import logging
from django.db.models.signals import post_delete
from django.dispatch import receiver, Signal
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from main.models import (StaffStatus, User)

logger = logging.getLogger('django')

update_queue = Signal()
channel_layer = get_channel_layer()


@receiver(update_queue, sender=None)
def send_update_signal(sender, **kwargs):
    """
    Send update queue signal to all staff when a student entered the waiting queue.

    :param sender:
    :param kwargs:
    :return:
    """
    try:
        async_to_sync(channel_layer.group_send)(
            'staff', {
                'type': 'refresh_chat_queue',
                'content': {
                    'type': 'update_queue'
                }
            }
        )
    except Exception as e:
        logger.warning(e)

@receiver(post_delete, sender=User)
def delete_staff(sender, instance, *args, **kwargs):
    """ Deletes staff status files on `post_delete` """
    if instance.netid:
        logger.info("Delete staff after user deleted")
        try:
            staff = StaffStatus.objects.get(staff_netid=instance.netid)
        except StaffStatus.DoesNotExist:
            logger.warning("Staff does not exist.")
            return
        staff.delete()
        logger.info("Staff deleted.")