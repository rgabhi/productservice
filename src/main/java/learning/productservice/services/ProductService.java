package learning.productservice.services;

import com.fasterxml.jackson.databind.deser.ResolvableDeserializer;
import learning.productservice.dtos.FakeStoreProductDto;
import learning.productservice.exceptions.ProductNotCreatedException;
import learning.productservice.exceptions.ProductNotFoundException;
import learning.productservice.models.Product;
import org.springframework.http.ResponseEntity;

import java.util.List;

public interface ProductService {
    public ResponseEntity<Product> getSingleProduct(Long id) throws ProductNotFoundException;
    public ResponseEntity<Product> addProduct(FakeStoreProductDto fakeStoreProductDto) throws ProductNotCreatedException;
    public ResponseEntity<List<Product>> getAllProducts() throws ProductNotFoundException;
    public ResponseEntity<Product> updateProduct(Long id, FakeStoreProductDto fakeStoreProductDto);
    public ResponseEntity<Product> replaceProduct(Long id, FakeStoreProductDto fakeStoreProductDto);
    public ResponseEntity<Product> deleteProduct(Long id);

}
