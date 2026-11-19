package learning.productservice.services;

import learning.productservice.dtos.FakeStoreProductDto;
import learning.productservice.models.Category;
import learning.productservice.models.Product;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;

@Service
public class FakeProductCategoryService implements CategoryService{
    private RestTemplate restTemplate;
    @Autowired
    FakeProductCategoryService(RestTemplate restTemplate){
        this.restTemplate = restTemplate;
    }

    private Product convertFakeStoreProductToProduct(FakeStoreProductDto fakeStoreProductDto){
        Product product = new Product();
        product.setId(fakeStoreProductDto.getId());
        product.setTitle(fakeStoreProductDto.getTitle());
        product.setPrice(fakeStoreProductDto.getPrice());
        product.setDescription(fakeStoreProductDto.getDescription());
        product.setImageUrl(fakeStoreProductDto.getImage());
        product.setCategory(new Category());
        product.getCategory().setName(fakeStoreProductDto.getCategory());
        return product;

    }
    @Override
    public ResponseEntity<List<Product>> getInCategory(String name) {
        FakeStoreProductDto[] fakeStoreProductDtos = restTemplate.getForObject("https://fakestoreapi.com/products/category/" +name, FakeStoreProductDto[].class);
        List<Product> productList= new ArrayList<>();
        for(int i = 0; i < fakeStoreProductDtos.length; i++){
            productList.add(convertFakeStoreProductToProduct(fakeStoreProductDtos[i]));
        }
        return new ResponseEntity<>(productList, HttpStatus.OK);
    }

    @Override
    public ResponseEntity<List<Category>> getAllCategories() {
        String[] categoryList = restTemplate.getForObject("https://fakestoreapi.com/products/categories", String[].class);
        List<Category> categories = new ArrayList<>();
        for(int i = 0; i < categoryList.length; i++){
            Category category = new Category();
            category.setName(categoryList[i]);
            categories.add(category);
        }
        return new ResponseEntity<>(categories, HttpStatus.OK);
    }
}
