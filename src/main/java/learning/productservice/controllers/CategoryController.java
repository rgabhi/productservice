package learning.productservice.controllers;

import learning.productservice.models.Category;
import learning.productservice.models.Product;
import learning.productservice.services.CategoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/products")
public class CategoryController {

    CategoryService categoryService;

    @Autowired
    CategoryController(CategoryService categoryService){
        this.categoryService = categoryService;
    }

    @GetMapping("/category/{name}")
    public ResponseEntity<List<Product>> getInCategory( @PathVariable("name") String name){
        return categoryService.getInCategory(name);
    }

    @GetMapping("/categories")
    public  ResponseEntity<List<Category>> getAllCategories(){
        return categoryService.getAllCategories();
    }
}
