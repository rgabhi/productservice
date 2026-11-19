package learning.productservice.dtos;

import lombok.Getter;
import lombok.Setter;

import java.io.Serializable;

@Getter
@Setter
public class FakeStoreProductDto implements Serializable {
    private long id;
    private String title;
    private double price;
    private String category;
    private String description;
    private String image;
}
