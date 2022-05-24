CREATE TABLE `accounts` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `stripe_id` VARCHAR(255) NULL COMMENT 'customer_id',
  `last_login` DATETIME NULL,
  `ip` VARCHAR(255) NULL,
  `disabled` TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  `created_date` DATETIME NOT NULL,
  `deleted_date` DATETIME NULL,
  PRIMARY KEY (`id`),
  UNIQUE `stripe_id` (`stripe_id`),
  INDEX `email` (`email`),
  INDEX `last_login` (`last_login`),
  INDEX `created_date` (`created_date`),
  INDEX `deleted_date` (`deleted_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `mail` (
  `account_id` INT UNSIGNED NOT NULL,
  `action` ENUM('reset_password','verify_email','update_payment') NOT NULL,
  `data` VARCHAR(255) NULL,
  `code` VARCHAR(255) NOT NULL,
  `created_date` DATETIME NOT NULL,
  PRIMARY KEY (`account_id`),
  UNIQUE `account_id__action` (`account_id`, `action`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `accounts_mfa` (
  `account_id` INT UNSIGNED NOT NULL,
  `2fa_hash` VARCHAR(255) NULL,
  `webauthn_pub_key` TEXT NULL,
  `webauthn_credential_id` TEXT NULL,
  `webauthn_sign_count` INT UNSIGNED NULL,
  `webauthn_rp_id` TEXT NULL,
  `created_date` DATETIME NOT NULL,
  PRIMARY KEY (`account_id`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `accounts_sentry` (
  `account_id` INT UNSIGNED NOT NULL,
  `sentry_dsn` VARCHAR(255) DEFAULT NULL,
  `sentry_enabled` TINYINT(1) UNSIGNED NOT NULL,
  PRIMARY KEY (`account_id`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `products` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `resources` INT NOT NULL,
  `stripe_id` VARCHAR(255) NULL COMMENT 'product_id',
  PRIMARY KEY (`id`),
  UNIQUE `name` (`name`),
  UNIQUE `resources` (`resources`),
  UNIQUE `stripe_id` (`stripe_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `prices` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `price` DOUBLE NOT NULL,
  `product_id` INT UNSIGNED NOT NULL,
  `stripe_id` VARCHAR(255) NULL COMMENT 'price_id',
  PRIMARY KEY (`id`),
  UNIQUE `stripe_id` (`stripe_id`),
  INDEX `product_id` (`product_id`),
  FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `licenses` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `account_id` INT UNSIGNED NOT NULL,
  `product_id` INT UNSIGNED NOT NULL,
  `access_key` VARCHAR(255) NOT NULL,
  `secret_key` VARCHAR(255) NOT NULL,
  `in_use` TINYINT(1) NOT NULL DEFAULT '0',
  `uuid` VARCHAR(255) DEFAULT NULL,
  `last_used` DATETIME DEFAULT NULL,
  `version` VARCHAR(255) NULL,
  `unregistered_date` DATETIME NULL,
  PRIMARY KEY (`id`),
  UNIQUE `account_id` (`account_id`),
  INDEX `product_id` (`product_id`),
  INDEX `in_use` (`in_use`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `subscriptions` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `account_id` INT UNSIGNED NOT NULL,
  `license_id` INT UNSIGNED NOT NULL,
  `product_id` INT UNSIGNED NOT NULL,
  `price_id` INT UNSIGNED NULL,
  `stripe_id` VARCHAR(255) NOT NULL COMMENT 'subscription_id',
  `created_date` DATETIME NOT NULL,
  `end_date` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `account_id` (`account_id`),
  INDEX `license_id` (`license_id`),
  INDEX `product_id` (`product_id`),
  INDEX `price_id` (`price_id`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`license_id`) REFERENCES `licenses` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`price_id`) REFERENCES `prices` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `payments` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `subscription_id` INT UNSIGNED NOT NULL,
  `created_date` DATETIME NOT NULL,
  `price` DOUBLE NOT NULL,
  `status` ENUM('paid','unpaid','expired') NOT NULL,
  `stripe_id` VARCHAR(255) NOT NULL COMMENT 'invoice_id',
  `next_payment_attempt` INT UNSIGNED NULL COMMENT 'unixtime',
  `invoice` TEXT NULL,
  PRIMARY KEY (`id`),
  INDEX `subscription_id` (`subscription_id`),
  UNIQUE `stripe_id` (`stripe_id`),
  FOREIGN KEY (`subscription_id`) REFERENCES `subscriptions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
