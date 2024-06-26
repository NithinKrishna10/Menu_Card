from fastcrud import FastCRUD

from ..models.advertisement import Advertisement
from ..schemas.advertisement import AdvertisementCreateInternal, AdvertisementDelete, AdvertisementUpdate, AdvertisementUpdateInternal

CRUDAdvertisement = FastCRUD[Advertisement, AdvertisementCreateInternal, AdvertisementUpdate, AdvertisementUpdateInternal, AdvertisementDelete]
crud_advertisement = CRUDAdvertisement(Advertisement)
