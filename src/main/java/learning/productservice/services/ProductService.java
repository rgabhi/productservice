package learning.productservice.services;

import learning.productservice.dtos.FakeStoreProductDto;
import learning.productservice.models.Product;

public interface ProductService {
    public Product getSingleProduct(Long id);
    public Product addSingleProduct(FakeStoreProductDto fakeStoreProductDto);
}
