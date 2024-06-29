from CRUDFastAPI import CRUDFastAPI

from ..models.product import Product , ProductPortion
from ..schemas.product import ProductCreateInternal, ProductDelete, ProductUpdate, ProductUpdateInternal , ProductPortionCreate,ProductPortionUpdate

    
CRUDProduct = CRUDFastAPI[Product, ProductCreateInternal, ProductUpdate, ProductUpdateInternal, ProductDelete]
crud_product = CRUDProduct(Product)

CRUDProductPortion = CRUDFastAPI[ProductPortion, ProductPortionCreate, ProductPortionUpdate,None,None]
crud_product_portion = CRUDProductPortion(ProductPortion)
