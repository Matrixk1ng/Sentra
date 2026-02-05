# IAM Role for EC2 to pull from ECR
resource "aws_iam_role" "ec2_role" {
  name = "sentra-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecr_read" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "sentra-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# Elastic IP (free when attached to running instance)
resource "aws_eip" "sentra" {
  domain = "vpc"
  tags = {
    Name = "sentra-eip"
  }
}

resource "aws_eip_association" "sentra" {
  instance_id   = aws_instance.sentra.id
  allocation_id = aws_eip.sentra.id
}

# EC2 Instance
resource "aws_instance" "sentra" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.sentra.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  associate_public_ip_address = true  
  subnet_id                   = data.aws_subnet.default.id  

  root_block_device {
    volume_size = 30 # Free tier: up to 30GB
    volume_type = "gp2"
  }

  user_data = base64encode(templatefile("${path.module}/../scripts/user-data.sh", {
    aws_region           = var.aws_region
    account_id           = data.aws_caller_identity.current.account_id
    youtube_api_key      = var.youtube_api_key
    bluesky_handle       = var.bluesky_handle
    bluesky_app_password = var.bluesky_app_password
    reddit_client_id     = var.reddit_client_id
    reddit_client_secret = var.reddit_client_secret
    postgres_password    = var.postgres_password
    SWAP_SIZE_GB         = 2
  }))

  tags = {
    Name = "sentra-server"
  }

  lifecycle {
    create_before_destroy = true
  }
}
