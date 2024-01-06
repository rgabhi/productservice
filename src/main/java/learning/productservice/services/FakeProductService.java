package learning.productservice.services;

import learning.productservice.dtos.FakeStoreProductDto;
import learning.productservice.models.Category;
import learning.productservice.models.Product;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class FakeProductService implements ProductService {

    private RestTemplate restTemplate;
    @Autowired
    FakeProductService(RestTemplate restTemplate){
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
    public Product getSingleProduct(Long id){
        FakeStoreProductDto productDto = restTemplate.getForObject("https://fakestoreapi.com/products/" + id, FakeStoreProductDto.class);
        return convertFakeStoreProductToProduct(productDto);
    }
    @Override
    public  Product addSingleProduct(FakeStoreProductDto fakeStoreProductDto){
        HttpEntity<FakeStoreProductDto> request = new HttpEntity<>(fakeStoreProductDto);
        FakeStoreProductDto productDto = restTemplate.postForObject("https://fakestoreapi.com/products", request, FakeStoreProductDto.class);
        return convertFakeStoreProductToProduct(productDto);
    }

}
