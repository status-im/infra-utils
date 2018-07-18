# Usage

There's no easy way of getting IDs of images in Alibabna Cloud so just do this:

```bash
terraform apply
terraform show
```

# Issues

We can't use Terraform `output` because it's broken for Alibaba data source:
https://github.com/alibaba/terraform-provider/issues/548
