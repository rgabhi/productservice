package learning.productservice.services;

import com.fasterxml.jackson.databind.deser.ResolvableDeserializer;
import learning.productservice.dtos.FakeStoreProductDto;
import learning.productservice.exceptions.ProductNotCreatedException;
import learning.productservice.exceptions.ProductNotFoundException;
import learning.productservice.models.Product;
import org.springframework.http.ResponseEntity;

import java.util.List;

public interface ProductService {
    public Product getSingleProduct(Long id) throws ProductNotFoundException;
    public Product addProduct(Product product) throws ProductNotCreatedException;
    public List<Product> getAllProducts() throws ProductNotFoundException;
    public Product updateProduct(Long id, Product product) throws ProductNotFoundException;
    public Product replaceProduct(Long id, Product product) throws ProductNotFoundException;
    public void deleteProduct(Long id);

}
