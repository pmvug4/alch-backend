from yoyo import step

__depends__ = {'0000.extension'}


steps = [
    step(
        """
            CREATE TABLE user_groups(
                id INT PRIMARY KEY,
                name VARCHAR(15) NOT NULL UNIQUE
            );
            
            INSERT INTO user_groups(id, name) VALUES (1, 'player');
            
            
            CREATE TABLE users(
                id SERIAL PRIMARY KEY,
                uuid UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
                
                group_id INT NOT NULL REFERENCES user_groups(id),
                
                email VARCHAR(127),
                password_hash VARCHAR(255),

                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP,
                deleted_at TIMESTAMP
            );
            CREATE UNIQUE INDEX ui_users ON users(email, deleted_at);
            
            CREATE TABLE email_verifications(
                id SERIAL PRIMARY KEY,
                key UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
                email VARCHAR(127) NOT NULL,
                code VARCHAR(7) NOT NULL,
                attempts_left INT NOT NULL,
                verified BOOL NOT NULL DEFAULT false,
                valid_until TIMESTAMP NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT now()
            );
            
            
            CREATE TABLE auth_session_platforms(
                id INT PRIMARY KEY,
                name VARCHAR(31) NOT NULL UNIQUE
            );
            
            INSERT INTO auth_session_platforms (id, name) VALUES 
                (1, 'mobile_android_app'),
                (2, 'mobile_ios_app'),
                (10, 'web')
            ;            

            CREATE TABLE auth_sessions(
                id SERIAL PRIMARY KEY,
                uuid UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
                user_id INT NOT NULL REFERENCES users(id),
                platform VARCHAR(31) NOT NULL REFERENCES auth_session_platforms(name),
                presign BOOL NOT NULL,
                
                refresh_token UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
                fcm_token VARCHAR(127),                
               
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP,
                revoked_at TIMESTAMP
            );
        """,
        """
            DROP TABLE auth_sessions;
            DROP TABLE auth_session_platforms;
            DROP TABLE email_verifications;
            DROP TABLE users;
            DROP TABLE user_groups;
        """
    )
]
