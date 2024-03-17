package learning.productservice.commons;

import learning.productservice.dtos.UserDto;
import org.apache.catalina.User;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class AuthenticationCommons {
    RestTemplate restTemplate;
    public AuthenticationCommons(RestTemplate restTemplate){
        this.restTemplate = restTemplate;
    }
    public UserDto validateToken(String token){
        ResponseEntity<UserDto> response = restTemplate.postForEntity("http://localhost:8181/users/validate" + token,
                null,
                UserDto.class);
        if(response.getBody() == null)return null;
        return response.getBody();
    }
}
