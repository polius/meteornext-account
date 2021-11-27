CREATE TABLE `accounts` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(191) NOT NULL,
  `password` VARCHAR(191) NOT NULL,
  `stripe_id` VARCHAR(191) NULL COMMENT 'customer_id',
  `last_login` DATETIME NULL,
  `ip` VARCHAR(191) NULL,
  `disabled` TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  `created` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `email` (`email`),
  INDEX `last_login` (`last_login`),
  INDEX `disabled` (`disabled`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `mail` (
  `account_id` INT UNSIGNED NOT NULL,
  `action` ENUM ('reset_password','verify_email') NOT NULL,
  `data` VARCHAR(191) NULL,
  `code` VARCHAR(191) NOT NULL,
  `created` DATETIME NOT NULL,
  PRIMARY KEY (`account_id`),
  UNIQUE `account_id__action` (`account_id`, `action`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `accounts_mfa` (
  `account_id` INT UNSIGNED NOT NULL,
  `2fa_hash` VARCHAR(191) NULL,
  `webauthn_ukey` TEXT NULL,
  `webauthn_pub_key` TEXT NULL,
  `webauthn_credential_id` TEXT NULL,
  `webauthn_sign_count` INT UNSIGNED NULL,
  `webauthn_rp_id` TEXT NULL,
  `created` DATETIME NOT NULL,
  PRIMARY KEY (`account_id`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `products` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `resources` INT NOT NULL,
  `price` DOUBLE NOT NULL COMMENT 'Reference value',
  `stripe_id` VARCHAR(191) NULL COMMENT 'product_id',
  PRIMARY KEY (`id`),
  UNIQUE `stripe_id` (`stripe_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

INSERT INTO `products` (`resources`, `price`, `stripe_id`) VALUES
(1, 0, NULL),
(5, 12.5, 'price_1JxaCAC4ZmM6nJCB'),
(10, 24, NULL),
(25, 57.5, NULL),
(50, 110, NULL),
(100, 210, NULL),
(200, 400, NULL),
(300, 570, NULL),
(400, 720, NULL),
(500, 850, NULL),
(750, 1200, NULL),
(1000, 1500, NULL),
(2000, 2800, NULL),
(3000, 3900, NULL),
(4000, 4800, NULL),
(5000, 5500, NULL),
(-1, 8200, NULL);

CREATE TABLE `licenses` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `account_id` INT UNSIGNED NOT NULL,
  `product_id` INT UNSIGNED NOT NULL,
  `access_key` VARCHAR(191) NOT NULL,
  `secret_key` VARCHAR(191) NOT NULL,
  `in_use` TINYINT(1) NOT NULL DEFAULT '0',
  `uuid` VARCHAR(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_used` DATETIME DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `account_id` (`account_id`),
  INDEX `product_id` (`product_id`),
  INDEX `expiration` (`expiration`),
  INDEX `in_use` (`in_use`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE
  FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `subscriptions` (
  `account_id` INT UNSIGNED NOT NULL,
  `product_id` INT UNSIGNED NOT NULL,
  `stripe_id` VARCHAR(191) NOT NULL COMMENT 'subscription_id',
  `date` DATETIME NOT NULL,
  PRIMARY KEY (`account_id`, `product_id`),
  UNIQUE `account_id` (`account_id`),
  INDEX `product_id` (`product_id`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `payments` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `account_id` INT UNSIGNED NOT NULL,
  `product_id` INT UNSIGNED NOT NULL,
  `date` DATETIME NOT NULL,
  `price` INT UNSIGNED NOT NULL,
  `status` ENUM('success','error') NOT NULL,
  `stripe_id` VARCHAR(191) NOT NULL COMMENT 'invoice_id',
  `invoice` TEXT NULL,
  PRIMARY KEY (`id`),
  INDEX `account_id` (`account_id`),
  INDEX `product_id` (`product_id`),
  UNIQUE `stripe_id` (`stripe_id`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;