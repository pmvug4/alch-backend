from yoyo import step

__depends__ = {'20240320_a.users'}


steps = [
    step(
        """ 
            CREATE TABLE media_type(
                id INT PRIMARY KEY,
                name VARCHAR(31) NOT NULL UNIQUE
            );
 
            INSERT INTO media_type(id, name) VALUES
                (1, 'avatar'),
                (5, 'element')
            ;
 
            CREATE TABLE media(
                id SERIAL PRIMARY KEY,
                uuid UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
 
                owner_uuid UUID,
                type_id INT NOT NULL REFERENCES media_type(id),
                internal_path VARCHAR(511) NOT NULL,
                public_url VARCHAR(511) NOT NULL,
 
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                deleted_at TIMESTAMP
            );
            CREATE UNIQUE INDEX ui_media(internal_path, public_url, deleted_at);
        """,
        """
            DROP TABLE media;
            DROP TABLE media_type;
        """
    ),
    step(
        """
            CREATE TABLE player(
                id SERIAL PRIMARY KEY,
                uuid UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
                user_id INT NOT NULL REFERENCES users(id),

                created_at TIMESTAMP NOT NULL DEFAULT now(),
                deleted_at TIMESTAMP
            );
            CREATE UNIQUE INDEX ui_player(user_id, deleted_at);
            
            CREATE TABLE player_info(
                id SERIAL PRIMARY KEY,
                player_id INT UNIQUE NOT NULL REFERENCES player(id),
                
                nickname VARCHAR(63) NOT NULL,
                avatar_uuid UUID REFERENCES media(uuid),

                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP
            );
            
            CREATE TABLE player_balance(
                id SERIAL PRIMARY KEY,
                player_id INT UNIQUE NOT NULL REFERENCES player(id),
                
                potions MEDIUMINT NOT NULL,
                stones MEDIUMINT NOT NULL,
                
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP
            );
            
            CREATE TYPE player_balance_transaction_reason AS ENUM(
                'game',
                'video_watched',
                'bought_stones',
                'top_up',
                'bought_vip',
                'other'
            );

            CREATE TABLE player_balance_transactions(
                id SERIAL PRIMARY KEY,
                uuid UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
                player_id INT NOT NULL REFERENCES player(id),
                
                reason player_balance_transaction_reason NOT NULL,
                stones_delta MEDIUMINT NOT NULL DEFAULT 0,
                potions_delta MEDIUMINT NOT NULL DEFAULT 0,
                
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            
            CREATE TABLE player_subscription(
                id SERIAL PRIMARY KEY,
                player_id INT UNIQUE NOT NULL REFERENCES player(id),
                
                is_vip BOOL NOT NULL DEFAULT FALSE,
                vip_until TIMESTAMP,
                    
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP
            ); 
        """
    )
]
