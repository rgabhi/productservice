package learning.productservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching
public class ProductserviceApplication {

    public static void main(String[] args) {

        SpringApplication.run(ProductserviceApplication.class, args);
    }

}
