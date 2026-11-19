package learning.productservice.services;

import learning.productservice.models.Category;
import learning.productservice.models.Product;
import org.springframework.http.ResponseEntity;

import java.util.List;

public interface CategoryService {
    public ResponseEntity<List<Product>> getInCategory(String name);
    public ResponseEntity<List<Category>> getAllCategories();

}
