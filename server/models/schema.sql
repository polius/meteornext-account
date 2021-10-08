CREATE TABLE `accounts` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(191) NOT NULL,
  `password` VARCHAR(191) NOT NULL,
  `last_login` DATETIME NULL,
  `ip` VARCHAR(191) NULL,
  `disabled` TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  `deleted` TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  `created_at` DATETIME NOT NULL,
  `deleted_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `email` (`email`),
  INDEX `last_login` (`last_login`),
  INDEX `disabled` (`disabled`),
  INDEX `deleted` (`deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `accounts_mfa` (
  `account_id` INT UNSIGNED NOT NULL,
  `2fa_hash` VARCHAR(191) NULL,
  `webauthn_ukey` TEXT NULL,
  `webauthn_pub_key` TEXT NULL,
  `webauthn_credential_id` TEXT NULL,
  `webauthn_sign_count` INT UNSIGNED NULL,
  `webauthn_rp_id` TEXT NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`account_id`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `licenses` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `account_id` INT UNSIGNED NOT NULL,
  `key` VARCHAR(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expiration` DATETIME NULL,
  `resources` INT UNSIGNED NOT NULL,
  `in_use` TINYINT(1) NOT NULL DEFAULT '0',
  `uuid` VARCHAR(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_used` DATETIME DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `account_id` (`account_id`),
  INDEX `expiration` (`expiration`),
  INDEX `in_use` (`in_use`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `pricing` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `base` DOUBLE NOT NULL,
  `server` DOUBLE NOT NULL,
  `reduction` NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `billing` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `license_id` INT UNSIGNED NOT NULL,
  `price` DOUBLE NOT NULL,
  `purchase_date` DATETIME NOT NULL,
  `payment_received` DATETIME NULL,
  `status` ENUM('pending','success','error') NOT NULL,
  `error` TEXT NULL,
  PRIMARY KEY (`id`),
  INDEX `license_id` (`license_id`),
  FOREIGN KEY (`license_id`) REFERENCES `licenses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;