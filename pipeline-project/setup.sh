#!/bin/bash

# Website Monitoring CI/CD Pipeline Setup Script

echo "🚀 Setting up Website Monitoring CI/CD Pipeline..."

# 1. Store GitHub token in AWS Secrets Manager
echo "📝 Step 1: Setting up GitHub token..."
echo "Please enter your GitHub Personal Access Token:"
read -s GITHUB_TOKEN

aws secretsmanager create-secret \
    --name "DevOps" \
    --description "GitHub token for CI/CD pipeline" \
    --secret-string "$GITHUB_TOKEN" \
    --region us-east-1

if [ $? -eq 0 ]; then
    echo "✅ GitHub token stored successfully!"
else
    echo "❌ Failed to store GitHub token. Please check your AWS credentials."
    exit 1
fi

# 2. Bootstrap CDK (if not already done)
echo "📦 Step 2: Bootstrapping CDK..."
cdk bootstrap

# 3. Install dependencies
echo "📚 Step 3: Installing dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

# 4. Test synthesis
echo "🧪 Step 4: Testing CDK synthesis..."
cdk synth

if [ $? -eq 0 ]; then
    echo "✅ Pipeline synthesis successful!"
    echo ""
    echo "🎉 Setup complete! You can now deploy with:"
    echo "   cdk deploy"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Update the repository name in pipeline_project_stack.py"
    echo "   2. Deploy the pipeline: cdk deploy"
    echo "   3. Check the CodePipeline console for your pipeline"
else
    echo "❌ Synthesis failed. Please check the errors above."
    exit 1
fi
