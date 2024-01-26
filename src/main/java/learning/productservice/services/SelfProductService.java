package learning.productservice.services;

import learning.productservice.exceptions.ProductNotCreatedException;
import learning.productservice.exceptions.ProductNotFoundException;
import learning.productservice.models.Category;
import learning.productservice.models.Product;
import learning.productservice.repositories.CategoryRepository;
import learning.productservice.repositories.ProductRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service("selfProductService")
public class SelfProductService implements ProductService{
    ProductRepository productRepository;
    CategoryRepository categoryRepository;

    @Autowired
    public SelfProductService(ProductRepository productRepository, CategoryRepository categoryRepository){
        this.productRepository = productRepository;
        this.categoryRepository = categoryRepository;
    }
    @Override
    public Product getSingleProduct(Long id) throws ProductNotFoundException {
        Optional<Product> productOptional = productRepository.findById(id);
        if(productOptional.isEmpty()) {
            throw new ProductNotFoundException("Product with id: " + id + " does not exist.");
        }
        return productOptional.get();
    }

    @Override
    public Product addProduct(Product product) throws ProductNotCreatedException {

        Optional<Category> categoryOptional = categoryRepository.findByName(product.getCategory().getName());
        if(categoryOptional.isEmpty()) {
            categoryRepository.save(product.getCategory());
        }else{
            product.setCategory(categoryOptional.get());
        }
        return productRepository.save(product);
    }

    @Override
    public List<Product> getAllProducts() throws ProductNotFoundException {
        return productRepository.findAll();
    }

    @Override
    public Product updateProduct(Long id, Product updateProduct) throws ProductNotFoundException {
        //find product by Id
        Optional<Product> productOptional = productRepository.findById(id);

        // If not found throw error
        if(productOptional.isEmpty()){
            throw new ProductNotFoundException("Product with id: " + id + " not found");
        }
        // else set the product and update respective parameters
        // from update product
        Product product = productOptional.get();
        if(updateProduct.getTitle() != null){
            product.setTitle(updateProduct.getTitle());
        }
        if(updateProduct.getCategory() != null){
            Optional<Category> categoryOptional = categoryRepository.findByName(updateProduct.getCategory().getName());
            if(categoryOptional.isEmpty()){
                product.setCategory(categoryRepository.save(updateProduct.getCategory()));
            }else{
                product.setCategory(categoryOptional.get());
            }

        }
        if(updateProduct.getDescription() != null){
            product.setDescription(updateProduct.getDescription());
        }
        if(updateProduct.getImageUrl() != null){
            product.setImageUrl(updateProduct.getImageUrl());
        }
        if(updateProduct.getPrice() != 0.0){
            updateProduct.setPrice(updateProduct.getPrice());
        }
        return productRepository.save(product);
    }

    @Override
    public Product replaceProduct(Long id, Product product) throws ProductNotFoundException {
        Optional<Product> productOptional = productRepository.findById(id);
        if(productOptional.isEmpty()){
            throw new ProductNotFoundException("Product with id: " + id + "not found");
        }else{
            product.setId(productOptional.get().getId());
            // check if category exists too or not;
            Optional<Category> categoryOptional = categoryRepository.findByName(
                    product.getCategory().getName());
            if(categoryOptional.isEmpty()){
                categoryRepository.save(product.getCategory());
            }
            else{
                product.setCategory(categoryOptional.get());
            }
        }
        return productRepository.save(product);
    }

    @Override
    public void deleteProduct(Long id) {
        productRepository.deleteById(id);
    }
}
