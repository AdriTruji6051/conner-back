
# Conner backend

Conner is a POS created for micro-enterprises that need a centralized POS service, but they didn´t has the opponrtunity to configurete an achieve a server, so, there comes Conner to improve they bussines.
It works as a local hosted programn that Connect several computers using the local network. You can easily add a printer service with the Conner printer service, and it ables you to use several printer and expand your bussines POS as you want.

- This is a preview of how it works. [Conner POS - Test page](https://adritruji6051.github.io/ConnerHost/)


## Author

- [@adriandDev](https://www.github.com/adritruji6051)


## Technologies 

- Python flask


## Create the databases 

Using the db_architecure.sql modules, copy and paste the diferen SQL commands to create
- data_base.db
- config.db
- history.db 
## Documentation

- If you want to take a look about how does it work, check the next document: [Conner docs](https://docs.google.com/document/d/14uFWKk8CKpCPhdW8aYYKkdY7IRwmmGYA2K6tv9guP_Q/edit?usp=sharing)


## API Reference quick start

#### Login and get token

```http
  POST /api/login
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `username` | `string` | **Required**. Username  |
| `password` | `string` | **Required**. Paswword  |

Returns your user TOKEN if loggin's succesed.

#### Register local printers

```http
  GET /api/init/new/
```

Try to get the printers (if there are) of the ip that has logged in, if the device have or not printers, returns the message.

#### Get products by description

```http
  GET /api/get/product/<string:search>
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `search` | `string` | **Required**. Description or code of the product to search  |

**Note ->** If the 'search' value is the code, it will return an array of lenght one with the only one, else, it will return an array with several values.

Try to get the printers (if there are) of the ip that has logged in, if the device have or not printers, returns the message.

#### Get product by ID

```http
  GET /api/get/product/id/<string:id>
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `id` | `string` | **Required**. Code of the product to search  |

Get the product by ID.

#### Get product by ID

```http
  GET /api/get/products/description/<string:description>
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `description` | `string` | **Required**. Description of the product to search  |

Retrieve the list of products that match with the description, it retrieve a list of products order by 'PRIORITY', ant fetch the data that matches with all the separated values at the string. 
- Example:  description = 'CH 66' or 'JAG CH' retrieves 'CHAROLA CHICA 66 JAGUAR' or another products that matches.

```http
  POST /api/create/product/
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `code` | `string` | **Required**. New product code  |
| `description` | `string` | **Required**. Product description  |
| `saleType` | `string` | **Required**. Sale type of the product 'U' for unities and 'D' for granel   |
| `cost` | `number` | **Required**, **None or Zero**. Product cost  |
| `salePrice` | `number` | **Required**. Product sale price  |
| `department` | `number` | **Required**, **None or Zero** Product department ID  |
| `wholesalePrice` | `number` | **Required**, **None or Zero** . wholesale price for the product  |
| `inventory` | `number` | **Required**, **Zero**. Product inventory  |
| `profitMargin` | `number` | **Required**, **Zero**. Profit margin (percentage)  |
| `parentCode` | `string` | **Required**, **None or Zero**. Parent code product (It will link his price to his parent product if get a product value there)  |

Create a new product.

```http
  POST /api/create/product/
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `originalCode` | `string` | **Required**. Previous product code for update  |
| `code` | `string` | **Required**. New product code  |
| `description` | `string` | **Required**. Product description  |
| `saleType` | `string` | **Required**. Sale type of the product 'U' for unities and 'D' for granel   |
| `cost` | `number` | **Required**, **None or Zero**. Product cost  |
| `salePrice` | `number` | **Required**. Product sale price  |
| `department` | `number` | **Required**, **None or Zero** Product department ID  |
| `wholesalePrice` | `number` | **Required**, **None or Zero** . wholesale price for the product  |
| `inventory` | `number` | **Required**, **Zero**. Product inventory  |
| `profitMargin` | `number` | **Required**, **Zero**. Profit margin (percentage)  |
| `parentCode` | `string` | **Required**, **None or Zero**. Parent code product (It will link his price to his parent product if get a product value there)  |
| `siblings` | `array` | **Required**, **None**. Siblings products code for update  |

Update the product that mathces with 'originalCode', also update the products that their codes are into the 'siblings' array, updating the 'cost', 'salePrice', 'wholesalePrice' and 'profitMargin' of all of them.


Delete product

```http
  DELETE /api/delete/product/id/<string:id>
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `id` | `string` | **Required**. Code of the product to delete  |




## Support

For complete docs, check the following link [check the full Conner docs](https://docs.google.com/document/d/14uFWKk8CKpCPhdW8aYYKkdY7IRwmmGYA2K6tv9guP_Q/edit?usp=sharing)
