package learning.productservice.dtos;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
public class UserDto {
        private String email;
        private String username;
        private String password;
        private List<Role> roles;
        private boolean isEmailVerified;
}
